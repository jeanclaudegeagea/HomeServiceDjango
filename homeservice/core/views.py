from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login  # Rename to avoid conflict
from django.contrib.auth import authenticate
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log successful signup
            print(f"New user registered: {user.email} (Username: {user.username})")
            print(f"New user registered: {user.email} (Username: {user.username})")
            
            # Auto-login after signup
            auth_login(request, user)  # Use auth_login with both request and user
            print(f"User {user.email} logged in successfully")
            print(f"User {user.email} logged in successfully")
            
            return redirect('dashboard')  # Redirect to dashboard or home page
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                auth_login(request, user)  # Use auth_login with both request and user
                # Log successful login
                print(f"User logged in: {email}")
                
                return redirect('dashboard')  # Redirect to dashboard or home page
            else:
                # This should not happen due to form validation, but added as a safeguard
                print(f"Login failed for: {email}")
                messages.error(request, "Invalid login credentials")
    else:
        form = UserLoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def dashboard_view(request):
    # Placeholder dashboard view
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'dashboard.html')



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
