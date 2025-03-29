# forms.py
from django import forms
from .models import User


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "user_type",
            "password",
        ]  # Include the fields you need

    # Optional: You can add custom validation or cleaning methods if needed
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
