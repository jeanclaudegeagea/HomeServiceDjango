from ..forms import UserRegistrationForm, UserLoginForm
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.shortcuts import render, redirect
from ..models import (
    User,
    Customer,
    ServiceProvider,
)
from django.contrib.auth import login, authenticate, logout


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
