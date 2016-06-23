from django import forms
from django.conf import settings

class RegisterForm(forms.Form):
    given_name = forms.CharField(label='Given Name', max_length=100)
    family_name = forms.CharField(label='Family Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)