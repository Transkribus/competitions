from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import LoginForm, RegisterForm, NEW_AFFILIATION_ID
from .forms import SubmitForm
from .models import Affiliation, Individual, Competition, Track, Subtrack
from .models import Submission, SubmissionStatus

def index(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    if request.user.is_authenticated():
        #TODO: Print a warning that we were already logged in, logout current user and proceed
        pass
        #return HttpResponseRedirect('/competitions/')
    if request.method == 'POST':
        if 'register' in request.POST:
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = User.objects.create_user(
                    username=register_form.cleaned_data['username'],
                    password=register_form.cleaned_data['password'],
                    email=register_form.cleaned_data['email'],
                    first_name=register_form.cleaned_data['first_name'],
                    last_name=register_form.cleaned_data['last_name'])

                affiliations_id = int(register_form.cleaned_data['affiliations'])
                affiliations_newstring = register_form.cleaned_data['new_affiliation']
                if(affiliations_id == NEW_AFFILIATION_ID):
                    #If the user selected 'Other'
                    if not affiliations_newstring:
                        #TODO: Redirect to some error page: New affiliation is unspecified
                        return HttpResponseRedirect('/competitions/')
                    affiliation = Affiliation.objects.create(name=affiliations_newstring)
                else:
                    if affiliations_newstring:
                        #TODO: Redirect to some error page: User specified a new affilation,
                        #      but also chose one from the list
                        return HttpResponseRedirect('/competitions/')                        
                    affiliation = Affiliation.objects.get(pk=affiliations_id)

                user.individual.shortbio = register_form.cleaned_data['shortbio']
                user.individual.affiliations.add(affiliation)
                #TODO: print a message saying that the user is created -- 
                # eventually will have to authenticate him by email
                return HttpResponseRedirect('/competitions/')
        elif 'login' in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(
                    username=login_form.cleaned_data['username'], 
                    password=login_form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        #TODO Redirect to success page
                    else:
                        #TODO Redirect to failure (disabled account)                        
                        pass
                else:
                    #TODO Redirect to failure (inexistent account)
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
    submit_form = SubmitForm(request.user)
    if request.method == 'POST':
        if not request.user.is_authenticated():
            #Normally this shouldn't be reachable anyway
            return render(request, 'competitions/submit.html', context)            
        submit_form = SubmitForm(request.user, request.POST, request.FILES)
        if submit_form.is_valid():
            # This is where code for all benchmarks will be called
            if Submission.objects.filter(
                subtrack=subtrack, 
                name=submit_form.cleaned_data['name']
                ):
                # Check if a the chosen name (slug) already exists                
                context['message'] = 'The method name already exists for this track. Please choose another name.'
                context['submit_form'] = SubmitForm(request.user)
                return render(request, 'competitions/submit.html', context)
            submission = Submission.objects.create(
                name = submit_form.cleaned_data['name'],
                method_info = submit_form.cleaned_data['method_info'],
                publishable = submit_form.cleaned_data['publishable'],
                subtrack = subtrack,
                resultfile = submit_form.cleaned_data['resultfile']
            )
            submission.submitter.add(request.user.individual)
            #TODO: Add the authenticated user and the coworkers here                       
            submission.save()
            for bmark in subtrack.benchmark_set.all():
                print(bmark)
                #TODO: Each cycle has to be run asynchronously
                submission_status = SubmissionStatus.objects.create(
                    submission=submission,
                    benchmark=bmark,
                    status="UNDEFINED"
                )
                #TODO: Call a python(?) function with a name based on bmark.name at this point
                # and update submission_status.numericalresult
                submission_status.numericalresult = ""
                submission_status.save()
                #TODO: Update status with the appropriate error msg if an error occurred
                submission_status.status = "COMPLETE"
                submission_status.save()
            context['message'] = 'Submission {} with id {} has been submitted sucesfully.'.format(submission.name, submission.id)
            return render(request, 'competitions/viewresults.html', context)
    context['submit_form'] = submit_form
    return render(request, 'competitions/submit.html', context)

def viewresults(request, competition_id, track_id, subtrack_id):
    #TODO: DRY ?
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
    return render(request, 'competitions/viewresults.html', context)