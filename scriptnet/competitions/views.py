from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_tables2 import RequestConfig

from .forms import LoginForm, RegisterForm, NEW_AFFILIATION_ID
from .forms import SubmitForm
from .models import Affiliation, Individual, Competition, Track, Subtrack
from .models import Submission, SubmissionStatus
from .tables import SubmissionTable, ScalarscoreTable, expandedScalarscoreTable, ManipulateMethodsTable
from . import evaluators

import threading
from json import loads

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
                if User.objects.filter(username=register_form.cleaned_data['username']):
                    errormessage_str_1 = _('The username')
                    errormessage_str_2 = _('already exists, please pick a different one.')
                    messages.add_message(request, messages.ERROR, 
                        '{} {} {}'.format(
                            errormessage_str_1,
                            register_form.cleaned_data['username'],
                            errormessage_str_2,
                        )
                    )
                    return HttpResponseRedirect('/competitions/#register')
                affiliations_id = int(register_form.cleaned_data['affiliations'])
                affiliations_newstring = register_form.cleaned_data['new_affiliation']
                if(affiliations_id == NEW_AFFILIATION_ID):
                    if not affiliations_newstring:
                        messages.add_message(request, messages.ERROR, _('Please specify your affiliation if it does not appear on the list.'))
                        return HttpResponseRedirect('/competitions/#register')
                    affiliation = Affiliation.objects.create(name=affiliations_newstring)
                else:
                    if affiliations_newstring:
                        messages.add_message(request, messages.ERROR, _('Please specify either an affiliation from the list, or "other" and specify a new affiliation.'))                        
                        return HttpResponseRedirect('/competitions/#register')
                    affiliation = Affiliation.objects.get(pk=affiliations_id)
                user = User.objects.create_user(
                    username=register_form.cleaned_data['username'],
                    password=register_form.cleaned_data['password'],
                    email=register_form.cleaned_data['email'],
                    first_name=register_form.cleaned_data['first_name'],
                    last_name=register_form.cleaned_data['last_name'])
                user.individual.shortbio = register_form.cleaned_data['shortbio']
                user.individual.affiliations.add(affiliation)
                user.individual.save()
                mails_sent = send_mail(
                    'Account creation at Scriptnet competitions',
                    """
Welcome to the Scriptnet competitions platform!

Sign in with your credentials (username: {}) at 
https://scriptnet.iit.demokritos.gr/competitions/#login 
to participate to the site competitions.




(c) 2016 READ Project
                    """.format(register_form.cleaned_data['username']),
                    settings.EMAIL_HOST_USER,
                    [user.email, settings.EMAIL_HOST_USER],
                    fail_silently=True,
                )
                #TODO: eventually will have to authenticate the new user by email
                messages.add_message(request, messages.SUCCESS, _('User {} has been created. Use your credentials to login.').format(user.username))
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
                        u = login_form.cleaned_data['username']                        
                        messages.add_message(request, messages.ERROR, _('User {} has been blocked. Please contact the administrator for details.').format(u))                                                
                        return HttpResponseRedirect('/competitions/#register')
                else:
                    u = login_form.cleaned_data['username']                    
                    messages.add_message(request, messages.ERROR, _('User {} does not exist. Please make sure that you have correctly typed your username, or register to create a new username.').format(u))                    
                    return HttpResponseRedirect('/competitions/#register')
    context = {
        'login_form': login_form,
        'register_form': register_form,
        'competitions': Competition.objects.filter(is_public=True),
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
                messages.add_message(request, messages.ERROR, _('The method name already exists for this track. Please choose another name.')) 
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
            # Determine which evaluator_functions we should call first, since
            # benchmarks are grouped according to the evaluator_function that ..evaluates them
            evalfunc_shouldcall = set()
            for bmark in subtrack.benchmark_set.all():
                evalfunc_shouldcall.add(bmark.evaluator_function)
            # Create a separate thread for each evaluator function that should be called
            for evalfunc in evalfunc_shouldcall:
                #TODO: Use a try-catch scheme to handle errors. 
                # Catches should fill in the status of 'submission_status'
                submission_status_set = set()
                for bmark in evalfunc.benchmark_set.all():
                    #Init result models (SubmissionStatus)
                    submission_status_set.add(SubmissionStatus.objects.create(
                        submission=submission,
                        benchmark=bmark,
                        status="UNDEFINED"
                    ))
                evaluator_function = getattr(evaluators, evalfunc.name, None)
                th = threading.Thread(name=str(evalfunc), target=evaluators.evaluator_worker, args=(evaluator_function, submission_status_set,))
                th.daemon = True
                th.start()
            messages.add_message(request, messages.SUCCESS, _('Submission {} with id {} has been submitted succesfully. ').format(submission.name, submission.id))
            return HttpResponseRedirect(reverse('viewresults', args=(competition_id, track_id, subtrack_id,)))
    context['submit_form'] = submit_form
    return render(request, 'competitions/submit.html', context)
    
def viewresults(request, competition_id, track_id, subtrack_id):
    competition, track, subtrack, context = get_objects_given_uniqueIDs(competition_id, track_id, subtrack_id)
    data = []
    if subtrack:
        all_benchmarks = subtrack.benchmark_set.all()
        all_submissions = subtrack.submission_set.all()
    elif track:
        all_benchmarks = set()
        all_submissions = set()
        for subt in track.subtrack_set.all():
            for b in subt.benchmark_set.all():
                all_benchmarks.add(b)
            for s in subt.submission_set.all():
                all_submissions.add(s)
    elif competition:
        #TODO: DRY? maybe create Model methods for these?
        all_benchmarks = set()
        all_submissions = set()
        for t in competition.track_set.all():
            for subt in t.subtrack_set.all():
                for b in subt.benchmark_set.all():
                    all_benchmarks.add(b)
                for s in subt.submission_set.all():
                    all_submissions.add(s)            
    for s in all_submissions:
        #Do not add submission on the list of show results if it is private, unless:
        # * the authenticated user is one of the authors
        # * the authenticated user is a superuser 
        if not s.publishable:
            if not request.user.is_authenticated():
                continue
            if request.user.is_superuser: 
                pass
            elif not request.user.individual in s.submitter.all():
                continue
        aff = set()
        for subm in s.submitter.all():
            for a in subm.affiliations.all():
                aff.add(a)
        results = s.submissionstatus_set.all()
        newrow = {
            'name': s.name,
            'method_info': s.method_info,
            'submitter': ', '.join(['{} {}'.format(subm.user.first_name, subm.user.last_name) for subm in s.submitter.all()]),
            'affiliation': ', '.join([a.name for a in aff]),
            'publishable': s.publishable,
        }
        if not subtrack:
            newrow['subtrack'] =  s.subtrack.name
        if not track:
            newrow['track'] = s.subtrack.track.name
        for b in all_benchmarks:
            try:
                nomen = b.name
                newrow[nomen] = loads(results.get(benchmark__name=nomen).numericalresult)
            except:
                newrow[nomen] = None
        data.append(newrow)
    #Create the table, excluding benchmarks that do not return a scalar value (e.g. pr-curve)
    extracolumns = [b.name for b in all_benchmarks if b.is_scalar]
    if not subtrack:
        extracolumns.insert(0, 'subtrack')
    if not track:
        extracolumns.insert(0, 'track')
    table = expandedScalarscoreTable(extracolumns)(data)
    RequestConfig(request).configure(table) #necessary for ordering and pagination
    context['table'] = table
    return render(request, 'competitions/viewresults.html', context)

def scoreboard(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    extracolumns = [
        'score',
    ]
    scoretable = {}
    for track in competition.track_set.all():
        scoretable[track.percomp_uniqueid] = expandedScalarscoreTable(extracolumns)(track.scoretable())
    context = {
        'competition': competition,
        'scoretable': scoretable,
    }
    return render(request, 'competitions/scoreboard.html', context)

def methodlist(request, competition_id):
    competition = get_object_or_404(Competition, pk=competition_id)
    if request.method == "POST":
        pks = request.POST.getlist("selection")
        selected_objects = Submission.objects.filter(pk__in=pks)
        #print(selected_objects)
        if 'publicize' in request.POST:
            for s in selected_objects:
                s.publishable = True
                s.save()
        elif 'privatize' in request.POST:
            for s in selected_objects:
                s.publishable = False
                s.save()
            print('Privatize pushed')
        elif 'delete' in request.POST:
            for s in selected_objects:
                messages.add_message(request, messages.SUCCESS, _('Submission {} has been deleted.').format(s))                
                s.delete()
    #myself = request.user.individual
    mymethods = Submission.objects.filter(submitter__user=request.user).filter(subtrack__track__competition=competition_id)
    table = ManipulateMethodsTable(mymethods)
    context = {
        'competition': competition,
        'table': table,
    }
    return render(request, 'competitions/methodlist.html', context)
    