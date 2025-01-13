from django import forms
from .models import Account
from django.contrib.auth.forms import UserCreationForm

class RegisterUser(UserCreationForm):
    class Meta:
        model =  Account
        fields = ['username', 'email', 'password1', 'password2']  # Include password1 and password2 fields
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Your Username Here'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Your Email'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Your Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Confirm Your Password'
            }),
        }

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = Account
#         fields = ['username', 'email']
        
       