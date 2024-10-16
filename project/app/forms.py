# forms.py
import re
from django import forms
from django.contrib.auth.models import User

from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    security_question = forms.CharField(max_length=255, required=True)
    security_answer = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Password strength validation: At least 8 characters, 1 uppercase, 1 lowercase, and 1 number
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Password must contain at least one number.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user
    
class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    security_answer = forms.CharField(max_length=255, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(),required=True)
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        security_answer = cleaned_data.get("security_answer")

        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)

            if profile.security_answer != security_answer:
                raise forms.ValidationError("Incorrect security answer.")
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")