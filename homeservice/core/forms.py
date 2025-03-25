# forms.py
from django import forms
from .models import User


class UserForm(forms.ModelForm):
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
    email = forms.EmailField()
    password = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Try to authenticate the user
            user = User.objects.filter(email=email).first()
            if not user:
                raise forms.ValidationError("No account found with this email")
                
            # Check if the password is correct
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")

        return cleaned_data