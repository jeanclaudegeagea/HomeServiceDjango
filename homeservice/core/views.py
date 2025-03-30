from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, CustomerRegistrationForm, ServiceProviderRegistrationForm, DocumentUploadForm
from .models import User, Customer, ServiceProvider, Specialization

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST, request.FILES)
        role = request.POST.get('role')
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            
            # Use full_phone if available, otherwise use phone
            phone = user_form.cleaned_data.get('full_phone') or user_form.cleaned_data.get('phone')
            user.phone = phone
            
            user.role = role
            user.save()
            
            if role == User.CUSTOMER:
                customer_form = CustomerRegistrationForm(request.POST)
                if customer_form.is_valid():
                    customer = customer_form.save(commit=False)
                    customer.user = user
                    customer.save()
                    messages.success(request, 'Customer account created successfully!')
                    login(request, user)
                    return redirect('customer_dashboard')
                else:
                    # If customer form is invalid, delete the user and show errors
                    user.delete()
                    messages.error(request, 'Error in customer details')
            
            elif role == User.SERVICE_PROVIDER:
                service_provider_form = ServiceProviderRegistrationForm(request.POST)
                if service_provider_form.is_valid():
                    service_provider = service_provider_form.save(commit=False)
                    service_provider.user = user
                    service_provider.save()
                    messages.success(request, 'Service provider account created! Please upload your documents.')
                    login(request, user)
                    return redirect('provider_upload_docs')
                else:
                    # If service provider form is invalid, delete the user and show errors
                    user.delete()
                    messages.error(request, 'Error in service provider details')
            else:
                messages.error(request, 'Invalid role selected')
                return render(request, 'accounts/register.html', {'form': user_form})
        
        # If user form is invalid, show errors
        return render(request, 'accounts/register.html', {'form': user_form})
    
    else:
        # Initialize specializations for the template if needed
        specializations = Specialization.objects.all()
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {
            'form': form,
            'specializations': specializations,
        })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.role == User.CUSTOMER:
                return redirect('customer_dashboard')
            elif user.role == User.SERVICE_PROVIDER:
                if user.serviceprovider.is_verified:
                    return redirect('provider_dashboard')
                else:
                    return redirect('provider_upload_docs')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

@login_required
def provider_upload_docs(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.provider = request.user.serviceprovider
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('provider_upload_docs')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'accounts/provider_upload_docs.html', {'form': form})

@login_required
def customer_dashboard(request):
    if request.user.role != User.CUSTOMER:
        return redirect('login')
    return render(request, 'accounts/customer_dashboard.html')

@login_required
def provider_dashboard(request):
    if request.user.role != User.SERVICE_PROVIDER:
        return redirect('login')
    if not request.user.serviceprovider.is_verified:
        return redirect('provider_upload_docs')
    return render(request, 'accounts/provider_dashboard.html')