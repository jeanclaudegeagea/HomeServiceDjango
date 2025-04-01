from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        (User.CUSTOMER, "Customer"),
        (User.SERVICE_PROVIDER, "Service Provider"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select, required=True)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20, required=False)
    full_phone = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
            "role",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
