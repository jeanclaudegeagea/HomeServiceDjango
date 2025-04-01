from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from django.utils import timezone
from .models import User, Customer, ServiceProvider, Specialization, Booking


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


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                login(request, user)
            except User.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                return redirect("home")  
            else:
                messages.error(request, "Invalid email or password")

        return render(request, "accounts/login.html", {"form": form})

    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect('login')

def profile(request):
    active_tab = request.GET.get('tab', 'upcoming')
    
    # Initialize empty querysets
    upcoming_bookings = []
    past_bookings = []
    
    if request.user.role == User.CUSTOMER:
        # Customer view
        customer = Customer.objects.get(user=request.user)
        upcoming_bookings = Booking.objects.filter(
            customer=customer,
            status__in=['pending', 'confirmed'],
            date__gte=timezone.now().date()
        ).order_by('date', 'time')[:5]
        
        past_bookings = Booking.objects.filter(
            customer=customer,
            status='completed',
            date__lt=timezone.now().date()
        ).order_by('-date', '-time')[:5]
        
    elif request.user.role == User.SERVICE_PROVIDER:
        # Service Provider view
        provider = ServiceProvider.objects.get(user=request.user)
        upcoming_bookings = Booking.objects.filter(
            provider=provider,
            status__in=['pending', 'confirmed'],
            date__gte=timezone.now().date()
        ).order_by('date', 'time')[:5]
        
        past_bookings = Booking.objects.filter(
            provider=provider,
            status='completed',
            date__lt=timezone.now().date()
        ).order_by('-date', '-time')[:5]
    
    # notifications = Notification.objects.filter(
    #     user=request.user
    # ).order_by('-created_at')[:5]
    
    context = {
        'active_tab': active_tab,
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        # 'notifications': notifications,
        'is_provider': request.user.role == User.SERVICE_PROVIDER,
    }
    
    return render(request, 'core/profile.html', context)

def customer_dashboard(request):
    return render(request, "accounts/customer_dashboard.html")


def provider_dashboard(request):
    return render(request, "accounts/provider_dashboard.html")


def base(request):
    return render(request, "core/base.html")


def home_view(request):
    context = {
        # 'service_categories': ServiceCategory.objects.all()[:6],
        # 'featured_providers': Provider.objects.filter(is_featured=True)[:3],
    }
    return render(request, 'core/home.html', context)
