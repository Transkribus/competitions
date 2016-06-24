from django import forms
from django.conf import settings
from .models import Affiliation

class RegisterForm(forms.Form):
    possible_affiliations = []
    for af in Affiliation.objects.all():
        possible_affiliations.append((af.id, af.name))
    first_name = forms.CharField(label='Given name', max_length=100)
    last_name = forms.CharField(label='Family name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    shortbio = forms.CharField(widget=forms.Textarea, label='Short biography (optional)')
	#avatar = forms.FileField(upload_to='uploads/avatars/', null=True, blank=True)
    affiliations = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=possible_affiliations
    )
    #TODO: Make this appear under conditions
    # Use the solution from http://codeinthehole.com/writing/conditional-logic-in-django-forms/ to do this?    
    new_affiliation = forms.CharField(required = False, label='Affiliation name (optional; specify if your affiliation does not show up above)', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)