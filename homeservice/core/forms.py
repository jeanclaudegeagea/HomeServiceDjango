from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError


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


class ChangePersonalInfoForm(forms.ModelForm):
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
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User  # or Profile
        fields = ["profile_image"]

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image", False)
        if image:
            if image.size > 4 * 1024 * 1024:  # 4MB limit
                raise ValidationError("Image file too large ( > 4MB )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")
