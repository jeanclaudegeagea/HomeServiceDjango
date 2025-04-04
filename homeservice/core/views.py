from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.utils import timezone
from .models import (
    User,
    Customer,
    ServiceProvider,
    Booking,
    ServiceProviderDocument,
    Specialization,
)
from .forms import (
    ProfileImageForm,
    ChangePersonalInfoForm,
    ServiceProviderDocumentForm,
)  # We'll create this form
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.db.models import Count
import os


@never_cache
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            password1 = form.cleaned_data.get("password1")
            password2 = form.cleaned_data.get("password2")

            if password1 != password2:
                form.add_error("password2", "Passwords do not match.")
                messages.error(request, "Passwords do not match.")
                return render(request, "accounts/register.html", {"form": form})

            phone = form.cleaned_data.get("full_phone") or form.cleaned_data.get(
                "phone"
            )
            user.phone = phone

            username = f"{user.first_name.lower()}{user.last_name.lower()}"
            username_base = username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            user.username = username
            user.role = int(form.cleaned_data["role"])
            user.set_password(password1)
            user.save()
            authenticate(request, username=username, password=password1)
            login(request, user)

            if user.role == User.CUSTOMER:
                Customer.objects.create(user=user)
                messages.success(request, "Customer account created successfully!")
                return redirect("home")
            else:
                ServiceProvider.objects.create(user=user)
                messages.success(
                    request,
                    "Service provider account created! Please complete your profile.",
                )
                return redirect("home")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@never_cache
def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.filter(email=email).first()

            if user:
                # Attempt to authenticate user
                user = authenticate(request, username=user.username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect("home")
                else:
                    messages.error(request, "Invalid email or password")
            else:
                messages.error(request, "No account found with this email")
        else:
            # Form is not valid
            messages.error(request, "Invalid email or password")

    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def signup_from_home(request):
    logout(request)
    return redirect("register")


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
            if document in provider.documents.all():
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


@never_cache
@login_required
def profile(request):
    active_tab = request.GET.get("tab", "upcoming")

    # Handle image upload
    if request.method == "POST" and "profile_image" in request.FILES:
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Redirect to avoid duplicate form submissions
    elif request.method == "POST" and "email" in request.POST:
        form = ChangePersonalInfoForm(
            request.POST, request.FILES, instance=request.user
        )

        if form.is_valid():
            user = request.user
            phone = form.cleaned_data.get("full_phone") or form.cleaned_data.get(
                "phone"
            )
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.phone = phone
            username = f"{user.first_name.lower()}{user.last_name.lower()}"
            username_base = username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1

            user.username = username

            user.save()

            messages.success(request, "Personal information updated successfully!")
            return redirect("profile")

        else:
            print(form.errors)
            messages.error(
                request, "There was an error updating your personal information."
            )

        return redirect("profile")  # Redirect to avoid duplicate form submissions
    else:
        form = ProfileImageForm()

    document_form = None
    documents = None
    if hasattr(request.user, "role"):
        if request.user.role == User.SERVICE_PROVIDER:
            if request.method == "POST" and "document_type" in request.POST:
                document_form = ServiceProviderDocumentForm(request.POST, request.FILES)
                if document_form.is_valid():
                    document = document_form.save(commit=False)
                    provider = ServiceProvider.objects.get(user=request.user)
                    document.save()
                    provider.documents.add(document)
                    messages.success(request, "Document uploaded successfully!")
                    return redirect("profile")
            else:
                document_form = ServiceProviderDocumentForm()

            provider = ServiceProvider.objects.get(user=request.user)
            documents = provider.documents.all()

    # Initialize empty querysets
    upcoming_bookings = []
    past_bookings = []

    if hasattr(request.user, "role"):
        if request.user.role == User.CUSTOMER:
            # Customer view
            customer = Customer.objects.get(user=request.user)
            upcoming_bookings = Booking.objects.filter(
                customer=customer,
                status__in=["pending", "confirmed"],
                date__gte=timezone.now().date(),
            ).order_by("date", "time")[:5]

            past_bookings = Booking.objects.filter(
                customer=customer, status="completed", date__lt=timezone.now().date()
            ).order_by("-date", "-time")[:5]

        elif request.user.role == User.SERVICE_PROVIDER:
            # Service Provider view
            provider = ServiceProvider.objects.get(user=request.user)
            upcoming_bookings = Booking.objects.filter(
                provider=provider,
                status__in=["pending", "confirmed"],
                date__gte=timezone.now().date(),
            ).order_by("date", "time")[:5]

            past_bookings = Booking.objects.filter(
                provider=provider, status="completed", date__lt=timezone.now().date()
            ).order_by("-date", "-time")[:5]

    isProvider = False

    if hasattr(request.user, "role"):
        isProvider = request.user.role == User.SERVICE_PROVIDER

    documents_list = list(
        documents.values("id", "document_type", "file", "issue_date", "expiry_date")
    )

    for document in documents_list:
        if document["issue_date"]:
            document["issue_date"] = document["issue_date"].strftime("%Y-%m-%d")
        if document["expiry_date"]:
            document["expiry_date"] = document["expiry_date"].strftime("%Y-%m-%d")

    documents_json = json.dumps(documents_list)

    years_of_experience = 0
    if hasattr(request.user, "serviceprovider"):
        years_of_experience = request.user.serviceprovider.years_of_experience

    specializations = Specialization.objects.all()
    specializations_list = list(specializations.values("id", "name", "description"))
    specializations_json = json.dumps(specializations_list)

    user_specializations = Specialization.objects.filter(
        serviceprovider__user=request.user
    ).values("id", "name", "description")
    user_specializations_list = list(user_specializations)
    user_specializations_list_json = json.dumps(user_specializations_list)

    context = {
        "active_tab": active_tab,
        "upcoming_bookings": upcoming_bookings,
        "past_bookings": past_bookings,
        "is_provider": isProvider,
        "form": form,  # Add the form to context
        "documents": documents_json,
        "document_form": document_form,
        "years_of_experience": years_of_experience,
        "specializations": specializations_json,
        "user_specializations": user_specializations_list_json,
    }

    return render(request, "core/profile.html", context)


def customer_dashboard(request):
    return render(request, "accounts/customer_dashboard.html")


def provider_dashboard(request):
    return render(request, "accounts/provider_dashboard.html")


@never_cache
def base(request):
    return render(request, "core/base.html")


@never_cache
def home_view(request):
    context = {
        # 'service_categories': ServiceCategory.objects.all()[:6],
        # 'featured_providers': Provider.objects.filter(is_featured=True)[:3],
    }
    return render(request, "core/home.html", context)


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
        if user.role == User.SERVICE_PROVIDER:
            try:
                service_provider = ServiceProvider.objects.get(user=user)

                # Delete all document files linked to this provider
                for doc in service_provider.documents.all():
                    if doc.file:
                        doc.file.delete(save=False)

                # Delete profile image if exists
                if user.profile_image:
                    user.profile_image.delete(save=False)

                # Delete the ServiceProvider and the User
                service_provider.delete()
                user.delete()

                # Clean up unused documents from DB and filesystem
                unused_docs = ServiceProviderDocument.objects.annotate(
                    provider_count=Count("serviceprovider")
                ).filter(provider_count=0)

                for doc in unused_docs:
                    if doc.file:
                        doc.file.delete(save=False)
                    doc.delete()

                logout(request)
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Account deleted successfully",
                        "redirect": "/login/",
                    },
                    status=200,
                )

            except ServiceProvider.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Service provider not found."},
                    status=404,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Only service providers can delete their accounts.",
                },
                status=403,
            )

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@login_required
def delete_profile_image(request):
    if request.method == "POST":
        user = request.user

        # Check if the user has a profile image
        if user.profile_image:
            # Delete the profile image from storage
            profile_image_path = user.profile_image.path
            user.profile_image.delete(save=False)  # Deletes the file from storage

            # Optional: If you want to remove it physically from the server (though it might be done by `delete()`):
            if os.path.exists(profile_image_path):
                os.remove(profile_image_path)

            # Optionally: Update the user profile field to `null` after deletion
            user.profile_image = None
            user.save()

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse(
                {"success": False, "error": "No profile image found."}, status=400
            )

    return JsonResponse(
        {"success": False, "error": "Invalid request method."}, status=405
    )
