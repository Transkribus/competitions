from django import forms
from django.conf import settings
from .models import Affiliation, Individual
from django.utils.translation import ugettext_lazy as _


NEW_AFFILIATION_ID = -1

class RegisterForm(forms.Form):
    #TODO: This code runs only once, when the server starts. Need to rerun when possible_affiliations changes
    # Do sth like submitform ?
    possible_affiliations = []
    for af in Affiliation.objects.order_by('name'):
        possible_affiliations.append((af.id, af.name))
    possible_affiliations.append((NEW_AFFILIATION_ID, 'Other'))

    first_name = forms.CharField(label=_('Given name'), max_length=100)
    last_name = forms.CharField(label=_('Family name'), max_length=100)
    email = forms.EmailField(label=_('Email'), max_length=100)
    shortbio = forms.CharField(required=False, widget=forms.Textarea, label=_('Short biography (optional)'))
    avatar = forms.FileField(label=_('Upload picture (optional)'), required=False)
    affiliations = forms.ChoiceField(
        required=False,
        widget=forms.Select,
        choices=possible_affiliations,
        label=_('Affiliation name')
    )
    #TODO: Make this appear under conditions
    # Use the solution from http://codeinthehole.com/writing/conditional-logic-in-django-forms/ to do this?    
    new_affiliation = forms.CharField(required = False, label=_('Affiliation name (specify here if your affiliation does not appear above)'), max_length=100)
    username = forms.CharField(label=_('Username'), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Password'), max_length=100)

class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label=_('Password'), max_length=100)

class ForgotpassForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=100)

class SubmitForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        possible_coauthors = []
        self.user = user
        super(SubmitForm, self).__init__(*args, **kwargs)    
        for coauth in Individual.objects.all():
            if(coauth.user.id != self.user.id):
                possible_coauthors.append((coauth.user.id, 
                "{} {} ({})".format(coauth.user.first_name, coauth.user.last_name, coauth.user.username)))
        self.fields['cosubmitters'] = forms.MultipleChoiceField(
            required=False,
            choices=possible_coauthors,
            label=_('Cosubmitters')
        )
        
    possible_coauthors = []        
    name = forms.SlugField(label=_('A short identifier for the method'), max_length = 20, allow_unicode = False)
    method_info = forms.CharField(required=False, widget=forms.Textarea, label=_('A short description of the method'), max_length = 300)
    publishable = forms.BooleanField(label=_('Show results for this method for everyone'), required=False, initial=True)
    resultfile = forms.FileField(label=_('Result file'))

class LanguageForm(forms.Form):
    language = forms.ChoiceField(label=_('Language'),choices=settings.LANGUAGES)

class WatchForm(forms.Form):
    pass

class SendMailForm(forms.Form):
    email_body = forms.CharField(required=True, widget=forms.Textarea, label=_('Fill in the email text here'), max_length = 3000)        