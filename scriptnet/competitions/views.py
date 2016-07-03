from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from .forms import LoginForm, RegisterForm, NEW_AFFILIATION_ID
from .forms import SubmitForm
from .models import Affiliation, Individual, Competition, Track, Subtrack
from .models import Submission, SubmissionStatus
from .tables import SubmissionTable
from . import evaluators

import threading

#TODO: Replace all hard-coded URLs with calls to 'reverse'

def get_objects_given_uniqueIDs(competition_id, track_id, subtrack_id):
    """
    This function is not a view, but a helper function that converts 
    unique-per-competition or unique-per-track ids into django objects.
    Also returns a context dictionary to pass directly to a template. 
    """
    competition = get_object_or_404(Competition, pk=competition_id)
    track = None #init
    subtrack = None #init
    if track_id is not None:        
        track = get_object_or_404(competition.track_set, percomp_uniqueid=track_id)
    if subtrack_id is not None:        
        subtrack = get_object_or_404(track.subtrack_set, pertrack_uniqueid=subtrack_id)
    context = {
        'competition': competition,
        'track': track,
        'subtrack': subtrack 
    }                        
    return competition, track, subtrack, context

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
                #TODO: Print some error message if the form contains error, like non-unique names etc
                user = User.objects.create_user(
                    username=register_form.cleaned_data['username'],
                    password=register_form.cleaned_data['password'],
                    email=register_form.cleaned_data['email'],
                    first_name=register_form.cleaned_data['first_name'],
                    last_name=register_form.cleaned_data['last_name'])
                affiliations_id = int(register_form.cleaned_data['affiliations'])
                affiliations_newstring = register_form.cleaned_data['new_affiliation']
                if(affiliations_id == NEW_AFFILIATION_ID):
                    if not affiliations_newstring:
                        messages.add_message(request, messages.ERROR, 'Please specify your affiliation, if it does not appear on the list.')
                        return HttpResponseRedirect('/competitions/')
                    affiliation = Affiliation.objects.create(name=affiliations_newstring)
                else:
                    if affiliations_newstring:
                        messages.add_message(request, messages.ERROR, 'Please specify either an affiliation from the list, or "other" and specify a new affiliation.')                        
                        return HttpResponseRedirect('/competitions/')                        
                    affiliation = Affiliation.objects.get(pk=affiliations_id)

                user.individual.shortbio = register_form.cleaned_data['shortbio']
                user.individual.affiliations.add(affiliation)
                #TODO: eventually will have to authenticate the new user by email
                messages.add_message(request, messages.SUCCESS, 'User {} has been created. Use your credentials to login.'.format(user.username))
                return HttpResponseRedirect('/competitions/#register')
        elif 'login' in request.POST:
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = authenticate(
                    username=login_form.cleaned_data['username'], 
                    password=login_form.cleaned_data['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
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
    competition, track, subtrack, context = get_objects_given_uniqueIDs(competition_id, track_id, subtrack_id)
    return render(request, 'competitions/competition.html', context)

def submit(request, competition_id, track_id, subtrack_id):
    competition, track, subtrack, context = get_objects_given_uniqueIDs(competition_id, track_id, subtrack_id)
    submit_form = SubmitForm(request.user)
    if request.method == 'POST':
        if not request.user.is_authenticated():
            #Normally this shouldn't be reachable anyway
            return render(request, 'competitions/submit.html', context)            
        submit_form = SubmitForm(request.user, request.POST, request.FILES)
        if submit_form.is_valid():
            if Submission.objects.filter(
                subtrack=subtrack, 
                name=submit_form.cleaned_data['name']
                ):                
                messages.add_message(request, messages.ERROR, 'The method name already exists for this track. Please choose another name.') 
                context['submit_form'] = SubmitForm(request.user)
                return render(request, 'competitions/submit.html', context)
            submission = Submission.objects.create(
                name = submit_form.cleaned_data['name'],
                method_info = submit_form.cleaned_data['method_info'],
                publishable = submit_form.cleaned_data['publishable'],
                subtrack = subtrack,
                resultfile = submit_form.cleaned_data['resultfile']
            )
            #TODO: Add the authenticated user and the coworkers here            
            submission.submitter.add(request.user.individual)
            submission.save()

            for bmark in subtrack.benchmark_set.all():
                #TODO: Use a try-catch scheme to handle errors. 
                # Catches should fill in the status of 'submission_status'
                submission_status = SubmissionStatus.objects.create(
                    submission=submission,
                    benchmark=bmark,
                    status="UNDEFINED"
                )
                evaluator_function = getattr(evaluators, bmark.name, None)
                th = threading.Thread(name=str(submission_status), target=evaluators.evaluator_worker, args=(evaluator_function, submission_status,))
                th.daemon = True
                th.start()
            messages.add_message(request, messages.SUCCESS, 'Submission {} with id {} has been submitted succesfully. '.format(submission.name, submission.id))
            return HttpResponseRedirect(reverse('viewresults', args=(competition_id, track_id, subtrack_id,)))
    context['submit_form'] = submit_form
    return render(request, 'competitions/submit.html', context)
    
def viewresults(request, competition_id, track_id, subtrack_id):
    competition, track, subtrack, context = get_objects_given_uniqueIDs(competition_id, track_id, subtrack_id)
    context['table'] = SubmissionTable(subtrack.submission_set.all())
    return render(request, 'competitions/viewresults.html', context)