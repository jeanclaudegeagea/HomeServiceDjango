from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm


def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user, but don't commit yet
            user = form.save(commit=False)
            # Set the password to make sure it's hashed
            user.set_password(form.cleaned_data["password"])
            # Save the user to the database
            user.save()

            # Optionally, show a success message
            messages.success(
                request, "You have successfully registered! Please log in."
            )

            # Redirect to login page (or anywhere you want)
            return redirect("login")
        else:
            # If the form is not valid, show errors
            messages.error(
                request, "There was an error in the form. Please check your inputs."
            )
    else:
        # If it's a GET request, just display the form
        form = UserRegistrationForm()

    return render(request, "core/signup.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # Authenticate the user using email and password
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # If user is found, log them in
                auth_login(request, user)
                return redirect("home")  # Redirect to the home page after login
            else:
                # If authentication fails
                messages.error(request, "Invalid username or password")

        # If the form is invalid, render the login page with errors
        return render(request, "core/login.html", {"form": form})

    else:
        form = UserLoginForm()

    return render(request, "core/login.html", {"form": form})


def base(request):
    return render(request, "core/base.html")


def home(request):
    return render(request, "core/home.html")


def services(request):
    return render(request, "core/services.html")


def providers(request):
    return render(request, "core/providers.html")


def book_service(request):
    return render(request, "core/book_service.html")
