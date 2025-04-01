from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.utils import timezone
from .models import User, Customer, ServiceProvider, Specialization, Booking
from .forms import ProfileImageForm  # We'll create this form
from django.views.decorators.cache import never_cache
from django.http import JsonResponse


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
            user = User.objects.get(email=email)

            # Attempt to authenticate user
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                # Authentication failed
                messages.error(request, "Invalid email or password")
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


@never_cache
def profile(request):
    active_tab = request.GET.get("tab", "upcoming")

    # Handle image upload
    if request.method == "POST" and "profile_image" in request.FILES:
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Redirect to avoid duplicate form submissions
    else:
        form = ProfileImageForm()

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

    context = {
        "active_tab": active_tab,
        "upcoming_bookings": upcoming_bookings,
        "past_bookings": past_bookings,
        "is_provider": isProvider,
        "form": form,  # Add the form to context
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
