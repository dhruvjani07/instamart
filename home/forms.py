"""
Forms used for registration and profile updates.
"""

import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile


class RegisterForm(UserCreationForm):
    """Form for user registration with validation."""

    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        """Validate username format."""
        username = self.cleaned_data.get("username")
        if not re.match(r'^\w+$', username):
            raise ValidationError("Only letters, numbers, and underscores allowed.")
        return username

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get("email")
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_phone(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get("phone")
        if not re.fullmatch(r'\+?[1-9]\d{1,14}$', phone):
            raise ValidationError("Phone must be in format +999999999 (up to 15 digits).")
        return phone

    def clean_password2(self):
        """Validate password match and strength."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Passwords do not match.")
        if len(password2) < 8 or not re.search(r'[a-z]', password2) \
                or not re.search(r'[A-Z]', password2) or not re.search(r'[0-9]', password2):
            raise ValidationError("Password must include uppercase, lowercase, and digits.")
        return password2


class UserUpdateForm(forms.ModelForm):
    """Form for updating user basic info."""

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile info."""

    class Meta:
        model = Profile
        fields = ['phone']
