from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
from django.http import HttpResponseRedirect

from .forms import RegisterForm
from .models import Competition, Track, Subtrack

def index(request):
    #return render(request, 'competitions/master.html')
    #all_competitions = Competition.objects.all()
    template = loader.get_template('competitions/master.html')
    context = {
        'competitions': Competition.objects.all(),
    }
    return HttpResponse(template.render(context, request))

def register(request):
    if request.user.is_authenticated():
        #TODO: Print a warning that we were already logged in, logout current user and proceed
        return HttpResponseRedirect('/competitions/')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            #TODO: Actually create the user
            # user = User.objects.create_user(form.cleaned_data['username'],password=form.cleaned_data['password'],email=form.cleaned_data['email'],first_name=form.cleaned_data['given_name'],last_name=form.cleaned_data['family_name'])
            #TODO print a message saying that the user is created -- eventually will have to authenticate him by email
            return HttpResponseRedirect('/competitions/')
    else:
        form = RegisterForm()

    context = {
        'register_form': form         
    }    
    return render(request, 'competitions/register.html', context)

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
