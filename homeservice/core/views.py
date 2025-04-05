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
    Service,
    Booking,
    ServiceProviderDocument,
    Specialization,
    Location,
)
from .forms import (
    ProfileImageForm,
    ChangePersonalInfoForm,
    ServiceProviderDocumentForm,
    ServiceForm,
)  # We'll create this form
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Q
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

        try:
            # If the user is a service provider
            if user.role == User.SERVICE_PROVIDER:
                service_provider = ServiceProvider.objects.get(user=user)

                # Delete all associated document files
                for doc in service_provider.documents.all():
                    if doc.file:
                        doc.file.delete(save=False)

                # Delete the ServiceProvider object
                service_provider.delete()

                # Clean up unused documents
                unused_docs = ServiceProviderDocument.objects.annotate(
                    provider_count=Count("serviceprovider")
                ).filter(provider_count=0)

                for doc in unused_docs:
                    if doc.file:
                        doc.file.delete(save=False)
                    doc.delete()

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


@login_required
def create_service(request):
    if request.user.role != User.SERVICE_PROVIDER:
        return redirect("home")

    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user.serviceprovider
            service.save()
            messages.success(request, "Service created successfully!")
            # return redirect('profile')
    else:
        form = ServiceForm()

    return render(request, "core/create_service.html", {"form": form})


def services_view(request):
    # Get all active services
    services = Service.objects.filter(is_active=True).select_related(
        "provider__user", "specialization"
    )

    # Get filter parameters from GET request
    specialization = request.GET.get("specialization")
    search_query = request.GET.get("search")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    location = request.GET.get("location")
    sort = request.GET.get("sort")

    if sort == "price_asc":
        services = services.order_by("price")
    elif sort == "price_desc":
        services = services.order_by("-price")
    elif sort == "name_asc":
        services = services.order_by("name")
    elif sort == "name_desc":
        services = services.order_by("-name")
    elif sort == "created_newest":
        services = services.order_by("-created_at")
    elif sort == "created_oldest":
        services = services.order_by("created_at")

    # Apply filters
    if specialization:
        services = services.filter(specialization__id=specialization)

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(specialization__name__icontains=search_query)
        )

    if min_price:
        services = services.filter(price__gte=min_price)

    if max_price:
        services = services.filter(price__lte=max_price)

    if location:
        services = services.filter(
            Q(city__icontains=location)
            | Q(state__icontains=location)
            | Q(country__icontains=location)
        )

    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all()

    context = {
        "services": services,
        "specializations": specializations,
        "search_query": search_query or "",
        "selected_specialization": int(specialization) if specialization else "",
        "min_price": min_price or "",
        "max_price": max_price or "",
        "location": location or "",
        "sort": sort or "",
    }

    return render(request, "core/services.html", context)


def providers_view(request):
    # Get all active service providers with their services count
    providers = ServiceProvider.objects.filter(user__is_active=True).annotate(
        service_count=Count("service", filter=Q(service__is_active=True))
    )

    # Get filter parameters from GET request
    specialization = request.GET.get("specialization")
    search_query = request.GET.get("search")
    min_experience = request.GET.get("min_experience")
    location = request.GET.get("location")

    # Apply filters
    if specialization:
        providers = providers.filter(specialization__id=specialization)

    if search_query:
        providers = providers.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(specialization__name__icontains=search_query)
        )

    if min_experience:
        providers = providers.filter(years_of_experience__gte=min_experience)

    if location:
        providers = providers.filter(
            Q(service__city__icontains=location)
            | Q(service__state__icontains=location)
            | Q(service__country__icontains=location)
        ).distinct()

    # Get all specializations for filter dropdown
    specializations = Specialization.objects.all()

    context = {
        "providers": providers,
        "specializations": specializations,
        "search_query": search_query or "",
        "selected_specialization": int(specialization) if specialization else "",
        "min_experience": min_experience or "",
        "location": location or "",
    }

    return render(request, "core/providers.html", context)


def service_provider_profile(request, id):
    # Retrieve the service provider related to the given user_id
    service_provider = ServiceProvider.objects.get(user_id=id)

    # Get the years_of_experience
    years_of_experience = service_provider.years_of_experience
    specializations = service_provider.specialization.all()

    services = (
        Service.objects.filter(provider=service_provider, is_active=True)
        .select_related("provider__user", "specialization")
        .order_by("-created_at")
    )

    context = {
        "service_provider": service_provider,
        "years_of_experience": years_of_experience,
        "specializations": specializations,
        "services": services,
    }

    return render(request, "core/service_provider_profile.html", context)
