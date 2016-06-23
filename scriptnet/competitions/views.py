from django.shortcuts import get_object_or_404, HttpResponse, render
from django.template import loader
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
    return HttpResponse("This should be the REGISTER landing page")

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
