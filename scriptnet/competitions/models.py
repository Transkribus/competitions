from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#The custom user class
class Individual(models.Model):
    #TODO: The user/individual will have to be authenticated by email eventually
	#TODO: This means that he _will_ be created, but a bool field here will check if he has been email-authenticated or not	
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	shortbio = models.TextField(editable=True, default="")
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.user.username)

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Individual.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User) 		

class Affiliation(models.Model):
	name = models.CharField(max_length = 50)
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	members = models.ManyToManyField(Individual)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

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
	public_data = models.FileField(upload_to='databases/', null=True) #Not sure if FileField is proper in this case
	#This will be test folds, non-visible to participants, usable only by the evaluation system
	private_data = models.FileField(upload_to='databases/', null=True) #Not sure if FileField is proper in this case
	def __str__(self):
		return '({}) {}, part of {} / {}'.format(self.id, self.name, self.track.competition.name, self.track.name)

class Submission(models.Model):
    #TODO: The submission will have to be authenticated by at least one individual per submitting institution to show up on the scoreboard eventually
	#TODO: Add a bool field that checks if the submission has been authenticated	
	method_info = models.CharField(max_length = 50)
	publishable = models.BooleanField(default=True)
	submitter = models.ManyToManyField(Individual)
	subtrack = models.ForeignKey(Subtrack, on_delete = models.CASCADE, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=True)
	resultfile = models.FileField(upload_to='uploads/submitted_results/', null=True) #Nullable because migrations complained, but it shouldnt ever be null
	def __str__(self):
		return '({}) {}'.format(self.id, self.method_info)

class Benchmark(models.Model):
	name = models.CharField(max_length = 50)
	#TODO: Have to add relations to other classes
	def __str__(self):
		return '({}) {}'.format(self.id, self.method_info)

