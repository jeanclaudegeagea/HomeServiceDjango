from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm

# Create your views here.


def base(request):
    return render(request, "core/base.html")


def login(request):
    return render(request, "core/login.html")


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
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
        form = UserForm()

    return render(request, "core/signup.html", {"form": form})


def home(request):
    return render(request, "core/home.html")


def services(request):
    return render(request, "core/services.html")


def providers(request):
    return render(request, "core/providers.html")


def book_service(request):
    return render(request, "core/book_service.html")
