from ..forms import (
    ProfileImageForm,
    ChangePersonalInfoForm,
    ServiceProviderDocumentForm,
)
from ..models import (
    User,
    Customer,
    ServiceProvider,
    Booking,
    Specialization,
)
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
import os


@never_cache
@login_required
def profile(request):
    active_tab = request.GET.get("tab", "upcoming")

    # Handle image upload
    if request.method == "POST" and "profile_image" in request.FILES:
        if request.user.profile_image:
            if os.path.exists(request.user.profile_image.path):
                os.remove(request.user.profile_image.path)
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
                created_at__gte=timezone.now().date(),
            ).order_by("created_at")[:5]

            past_bookings = Booking.objects.filter(
                customer=customer,
                status="completed",
                created_at__lt=timezone.now().date(),
            ).order_by("-created_at")[:5]

        elif request.user.role == User.SERVICE_PROVIDER:
            # Service Provider view
            provider = ServiceProvider.objects.get(user=request.user)
            upcoming_bookings = Booking.objects.filter(
                service__provider=provider,
                status__in=["pending", "confirmed"],
                created_at__gte=timezone.now().date(),
            ).order_by("created_at")[:5]

            past_bookings = Booking.objects.filter(
                service__provider=provider,
                status="completed",
                created_at__lt=timezone.now().date(),
            ).order_by("-created_at")[:5]

    isProvider = False
    isCustomer = False

    if hasattr(request.user, "role"):
        isProvider = request.user.role == User.SERVICE_PROVIDER
        isCustomer = request.user.role == User.CUSTOMER

    if isProvider:
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

    if isProvider:
        specializations = Specialization.objects.all()
        specializations_list = list(specializations.values("id", "name", "description"))
        specializations_json = json.dumps(specializations_list)

        user_specializations = Specialization.objects.filter(
            serviceprovider__user=request.user
        ).values("id", "name", "description")
        user_specializations_list = list(user_specializations)
        user_specializations_list_json = json.dumps(user_specializations_list)

    if isProvider:
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
    if isCustomer:
        customer = (
            Customer.objects.filter(user=request.user)
            .select_related("location")
            .first()
        )
        location = customer.location if customer else None
        location_list = (
            [
                location.address_line1,
                location.address_line2,
                location.city,
                location.state,
                location.postal_code,
                location.country,
            ]
            if location
            else []
        )
        location_list_json = json.dumps(location_list)

        context = {"location": location_list_json}

    return render(request, "core/profile.html", context)


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
