from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout

from .forms import LoginForm, RegisterForm
from .models import Competition, Track, Subtrack

def index(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    if request.user.is_authenticated():
        #TODO: Print a warning that we were already logged in, logout current user and proceed
        pass
        #return HttpResponseRedirect('/competitions/')
    if request.method == 'POST':
        if 'register' in request.POST:
            print("Register button")
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                #TODO: Actually create the user
                # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
                #TODO print a message saying that the user is created -- eventually will have to authenticate him by email
                return HttpResponseRedirect('/competitions/')
        elif 'login' in request.POST:
            print("Login button")            
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                #TODO Check if ok
                pass
    context = {
        'login_form': login_form,
        'register_form': register_form,
        'competitions': Competition.objects.all(),
    }
    return render(request, 'competitions/master.html', context)

def signout(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect('/competitions/')

def competition(request, competition_id, track_id, subtrack_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    track = None #init
    subtrack = None #init
    if track_id is not None:        
        track = get_object_or_404(competition.track_set, pk=track_id)
    if subtrack_id is not None:        
        subtrack = get_object_or_404(track.subtrack_set, pk=subtrack_id)
    context = {
        'competition': competition,
        'track': track,
        'subtrack': subtrack
    }
    return render(request, 'competitions/competition.html', context)

def submit(request, competition_id, track_id, subtrack_id):
	return HttpResponse("This site is to submit to a specific competition / track / subtrack")

def viewresults(request, competition_id, track_id, subtrack_id):
	return HttpResponse("This site is to view results of a specific competition / track / subtrack")
