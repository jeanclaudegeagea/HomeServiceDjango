from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Customer, ServiceProvider, Location, Specialization, ServiceProviderDocument

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        (User.CUSTOMER, 'Customer'),
        (User.SERVICE_PROVIDER, 'Service Provider'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20, required=False)
    full_phone = forms.CharField(widget=forms.HiddenInput(), required=False)  # For storing full international number
    profile_image = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'profile_image', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autocomplete': 'username'})
        self.fields['email'].widget.attrs.update({'autocomplete': 'email'})
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

class CustomerRegistrationForm(forms.ModelForm):
    address_line1 = forms.CharField(max_length=255)
    address_line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = Customer
        fields = []
        
    def save(self, commit=True):
        location = Location.objects.create(
            address_line1=self.cleaned_data['address_line1'],
            address_line2=self.cleaned_data['address_line2'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            postal_code=self.cleaned_data['postal_code'],
            country=self.cleaned_data['country']
        )
        customer = super().save(commit=False)
        customer.location = location
        if commit:
            customer.save()
        return customer

class ServiceProviderRegistrationForm(forms.ModelForm):
    years_of_experience = forms.IntegerField(min_value=0)
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = ServiceProvider
        fields = ['years_of_experience', 'specializations']
        
    def save(self, commit=True):
        service_provider = super().save(commit=False)
        if commit:
            service_provider.save()
            self.cleaned_data['specializations'] and service_provider.specialization.set(self.cleaned_data['specializations'])
        return service_provider

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = ServiceProviderDocument
        fields = ['document_type', 'file', 'issue_date', 'expiry_date']