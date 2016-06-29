from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from uuid import uuid4
from time import strftime

class Affiliation(models.Model):
	name = models.CharField(max_length = 50)
	#TODO: Use a unique identifier like in submission_path	
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

#The custom user class
class Individual(models.Model):
    #TODO: The user/individual will have to be authenticated by email eventually
	#TODO: This means that he _will_ be created, but a bool field here will check if he has been email-authenticated or not	
	user = models.OneToOneField(User, on_delete=models.CASCADE)	
	shortbio = models.TextField(editable=True, default="")
	affiliations = models.ManyToManyField(Affiliation)
	#TODO: Use a unique identifier like in submission_path	
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.user.username)

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Individual.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User) 		

class Competition(models.Model):
	organizer = models.ManyToManyField(Individual)
	name = models.CharField(max_length = 50)
	overview = models.TextField(editable=True, default="")
	newsfeed = models.TextField(editable=True, default="")
	important_dates = models.TextField(editable=True, default="")
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

class Track(models.Model):
	name = models.CharField(max_length = 50)
	overview = models.TextField(editable=True, default="")
	competition = models.ForeignKey(Competition, on_delete = models.CASCADE)
	def __str__(self):
		return '({}) {}, part of {}'.format(self.id, self.name, self.competition.name)

#Info about saving to a custom folder here: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload%5Fto
#and here: http://stackoverflow.com/questions/1190697/django-filefield-with-upload-to-determined-at-runtime
class Subtrack(models.Model):
	name = models.CharField(max_length = 50)
	track = models.ForeignKey(Track, on_delete = models.CASCADE)
	#This will normally be training+validation folds, visible to any registered user
	#TODO: Use a unique identifier like in submission_path
	public_data = models.FileField(upload_to='databases/', null=True, blank=True, default="") #Not sure if FileField is proper in this case
	#Organizers have the option of using a URL field here, in case they want to serve the public data themselves
	#If this is non-blank, it overrides the 'public_data' field
	public_data_external = models.URLField(null=True, blank=True, default="")
	#This will be test folds, non-visible to participants, usable only by the evaluation system
	#TODO: Use a unique identifier like in submission_path	
	private_data = models.FileField(upload_to='databases/', null=True) #Not sure if FileField is proper in this case
	def __str__(self):
		return '({}) {}, part of {} / {}'.format(self.id, self.name, self.track.competition.name, self.track.name)

def submission_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_.../<datestamp>/<random unique identifier>/filename
	return 'uploads/submitted_results/{}/{}/{}'.format(
		strftime("%Y_%m_%d"),
		uuid4().hex, 
		filename)

class Submission(models.Model):
    #TODO: The submission will have to be authenticated by at least one individual per submitting institution to show up on the scoreboard eventually
	#TODO: Add a bool field that checks if the submission has been authenticated
	name = models.SlugField(max_length = 20, null=False, blank=False, default="")
	method_info = models.TextField(editable=True, default="")
	publishable = models.BooleanField(default=True)
	submitter = models.ManyToManyField(Individual)
	#secondary_submitters = models.ManyToManyField(Individual, related_name="coworker_submission")
	subtrack = models.ForeignKey(Subtrack, on_delete = models.CASCADE, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=True)
	resultfile = models.FileField(upload_to=submission_path, null=True) #Nullable because migrations complained, but it shouldnt ever be null
	def __str__(self):
		return '({}) {}'.format(self.id, self.method_info)

class Benchmark(models.Model):
	#TODO: A python callable will be implicitly related to each submission.
	#	   The name of the callable will be based on the 'name' field of this model
	name = models.SlugField(max_length = 50, null=False, blank=False, default="")
	benchmark_info = models.TextField(editable=True, default="")
	subtracks = models.ManyToManyField(Subtrack)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

class SubmissionStatus(models.Model):
	class Meta:
		verbose_name_plural = 'submission status'
	POSSIBLE_STATUS = (
		('UNDEFINED', 'The processing state of the submission is undefined'),
		('PROCESSING', 'We are currently processing the submitted result'),		
		('ERROR_EVALUATOR', 'Could not call the related evaluator function'),
		('ERROR_GENERIC', 'An error has occured before processing could start'),
		('ERROR_PROCESSING', 'An error has occured during processing of the submitted result'),		
		('COMPLETE', 'The submitted result has been succesfully processed and a numerical result has been saved')
	)
	submission = models.ForeignKey(Submission, on_delete = models.CASCADE, null=True)
	benchmark = models.ForeignKey(Benchmark, on_delete = models.CASCADE, null=True)
	numericalresult = models.CharField(max_length = 100, null=False, blank=False, default="")
	status = models.CharField(max_length = 20, choices=POSSIBLE_STATUS, default='UNDEFINED')
	start_time = models.DateTimeField(auto_now_add=True, null=True)
	end_time = models.DateTimeField(auto_now=True, null=True)
	def __str__(self):
		return '({}/{}) [score={}] [{}]'.format(self.benchmark, self.id, self.numericalresult, self.status)