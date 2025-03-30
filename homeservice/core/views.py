from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import User, Customer, ServiceProvider, Specialization

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            phone = form.cleaned_data.get('full_phone') or form.cleaned_data.get('phone')
            user.phone = phone

            username = f"{user.first_name.lower()}{user.last_name.lower()}"
            username_base = username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
            user.username = username

            user.role = form.cleaned_data['role']            
            user.save()
            
            login(request, user)
            
            if user.role == User.CUSTOMER:
                Customer.objects.create(user=user)
                messages.success(request, 'Customer account created successfully!')
                return redirect('customer_dashboard')
            else:
                ServiceProvider.objects.create(user=user)
                messages.success(request, 'Service provider account created! Please complete your profile.')
                return redirect('provider_profile')
            
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    return render(request, 'accounts/login.html')