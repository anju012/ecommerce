from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

class AddForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','price','description','image']

class RegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']

     


class LoginForm(AuthenticationForm):
    pass