from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import (
    ServiceProvider,
    ServiceProviderDocument,
    Specialization,
    User,
    Customer,
    Location,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.db.models import Count
from django.contrib.auth import logout
import json
import os


@never_cache
def service_settings(request):
    # Render the partial content
    html_content = render(request, "serviceProvider/settings.html")
    return JsonResponse({"html": html_content.content.decode("utf-8")})


@never_cache
def customer_settings(request):
    # Render the partial content
    html_content = render(request, "customer/settings.html")
    return JsonResponse({"html": html_content.content.decode("utf-8")})


@login_required
def delete_document(request):
    if request.method == "POST":
        try:
            # Get the document ID from the POST data
            doc_id = request.POST.get("doc_id")
            # Fetch the document by ID
            document = ServiceProviderDocument.objects.get(id=doc_id)

            # Fetch the service provider associated with the current user
            provider = ServiceProvider.objects.get(user=request.user)

            # Check if the document belongs to the provider
            if document.provider == provider:  # Changed this line
                # If the document is associated with the provider, delete the file locally
                document_path = document.file.path
                # Delete the document file from the storage
                document.delete()

                # Optionally, you can delete the file physically from the filesystem if needed
                if os.path.exists(document_path):
                    os.remove(document_path)

                # Send a success message
                messages.success(request, "Document deleted successfully!")
            else:
                messages.error(request, "Document not associated with your profile!")

        except ServiceProviderDocument.DoesNotExist:
            messages.error(request, "Document not found!")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect("profile")


@csrf_exempt
@login_required
def update_experience(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            years = data.get("years_of_experience")

            if years is None or not str(years).isdigit():
                return JsonResponse(
                    {"success": False, "error": "Invalid years of experience"}
                )

            try:
                provider = ServiceProvider.objects.get(user=request.user)
                provider.years_of_experience = int(years)
                provider.save()
                return JsonResponse({"success": True})
            except ServiceProvider.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "User is not a service provider"}
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
@login_required
def add_specialization(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            spec_id = data.get("specialization_id")

            if not spec_id:
                return JsonResponse(
                    {"success": False, "error": "Specialization ID is required"}
                )

            try:
                specialization = Specialization.objects.get(id=spec_id)
                provider = ServiceProvider.objects.get(user=request.user)

                if provider.specialization.filter(id=spec_id).exists():
                    return JsonResponse(
                        {"success": False, "error": "Specialization already added"}
                    )

                provider.specialization.add(specialization)
                return JsonResponse(
                    {
                        "success": True,
                        "specialization_name": specialization.name,
                        "specialization_description": specialization.description,
                        "specialization_id": specialization.id,
                    }
                )
            except Specialization.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Specialization not found"}
                )
            except ServiceProvider.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "User is not a service provider"}
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
@login_required
def remove_specialization(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            spec_id = data.get("specialization_id")

            if not spec_id:
                return JsonResponse(
                    {"success": False, "error": "Specialization ID is required"}
                )

            try:
                specialization = Specialization.objects.get(id=spec_id)
                provider = ServiceProvider.objects.get(user=request.user)

                if not provider.specialization.filter(id=spec_id).exists():
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "Specialization not found in your profile",
                        }
                    )

                provider.specialization.remove(specialization)
                return JsonResponse({"success": True})
            except Specialization.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Specialization not found"}
                )
            except ServiceProvider.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "User is not a service provider"}
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
@login_required
def changePassword(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            password1 = data.get("password1")
            password2 = data.get("password2")

            if password1 != password2:
                return JsonResponse(
                    {"success": False, "error": "Passwords do not match"},
                )

            # Validate password using Django's built-in validators
            validate_password(password1, user=request.user)

            # Update password
            request.user.password = make_password(
                password1
            )  # Hash password before saving
            request.user.save()

            return JsonResponse(
                {"success": True, "message": "Password changed successfully"},
                status=200,
            )

        except ValidationError as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@csrf_exempt
@login_required
def deleteAccount(request):
    if request.method == "POST":
        user = request.user

        try:
            # If the user is a service provider
            if user.role == User.SERVICE_PROVIDER:
                service_provider = ServiceProvider.objects.get(user=user)

                # Get all documents associated with this provider
                provider_documents = ServiceProviderDocument.objects.filter(provider=service_provider)

                # Delete all associated document files
                for doc in provider_documents:
                    if doc.file:
                        doc.file.delete(save=False)
                    doc.delete()

                # Delete the ServiceProvider object
                service_provider.delete()

            # If the user is a customer
            elif user.role == User.CUSTOMER:
                customer = Customer.objects.get(user=user)

                # Delete associated location if exists
                if customer.location:
                    customer.location.delete()

                # Delete the Customer object
                customer.delete()

            else:
                return JsonResponse(
                    {"success": False, "error": "Invalid user role."},
                    status=403,
                )

            # Delete the profile image (if exists)
            if user.profile_image:
                user.profile_image.delete(save=False)

            # Delete the User account
            user.delete()

            # Logout the user
            logout(request)

            return JsonResponse(
                {
                    "success": True,
                    "message": "Account deleted successfully",
                    "redirect": "/login/",
                },
                status=200,
            )

        except (ServiceProvider.DoesNotExist, Customer.DoesNotExist):
            return JsonResponse(
                {"success": False, "error": "User not found."},
                status=404,
            )

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )

@csrf_exempt
@login_required
def updateLocation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract user and location data
            user = request.user
            address_line1 = data.get("address_line1", "").strip()
            address_line2 = data.get("address_line2", "").strip()
            city = data.get("city", "").strip()
            state = data.get("state", "").strip()
            postal_code = data.get("postal_code", "").strip()
            country = data.get("country", "").strip()

            # Validate required fields
            if (
                not address_line1
                or not city
                or not state
                or not postal_code
                or not country
            ):
                return JsonResponse(
                    {"success": False, "error": "Missing required fields"}, status=400
                )

            # Get or create customer record
            customer, created = Customer.objects.get_or_create(user=user)

            # Check if the customer has an existing location
            if customer.location:
                location = customer.location
            else:
                location = Location()

            # Update location fields
            location.address_line1 = address_line1
            location.address_line2 = address_line2
            location.city = city
            location.state = state
            location.postal_code = postal_code
            location.country = country
            location.save()

            # Link location to customer if not already linked
            if not customer.location:
                customer.location = location
                customer.save()

            return JsonResponse(
                {"success": True, "message": "Location updated successfully"},
                status=200,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "error": "Invalid JSON format"}, status=400
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )
