from django import forms
from django.conf import settings
from .models import Affiliation, Individual

NEW_AFFILIATION_ID = -1

class RegisterForm(forms.Form):
    possible_affiliations = []
    for af in Affiliation.objects.all():
        possible_affiliations.append((af.id, af.name))
    possible_affiliations.append((NEW_AFFILIATION_ID, 'Other'))
    
    first_name = forms.CharField(label='Given name', max_length=100)
    last_name = forms.CharField(label='Family name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    shortbio = forms.CharField(required=False, widget=forms.Textarea, label='Short biography (optional)')
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

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)

class SubmitForm(forms.Form):
    possible_coauthors = []
    for coauth in Individual.objects.all():
        #TODO: Make sure that the current user doesnt appear here
        possible_coauthors.append((coauth.user.id, coauth.user.username))

    slug = forms.SlugField(max_length = 20, allow_unicode = False)
    method_info = forms.CharField(required=False, widget=forms.Textarea, label='A short description of the method', max_length = 300)
    publishable = forms.BooleanField(label='Show results for this method for everyone', required=False)
    cosubmitters = forms.MultipleChoiceField(
        required=False,
        choices=possible_coauthors
    )
    #TODO: This creates a required field error no matter what,
    # possible solution https://docs.djangoproject.com/en/1.9/ref/forms/api/#binding-uploaded-files
    resultfile = forms.FileField(label='Result file')