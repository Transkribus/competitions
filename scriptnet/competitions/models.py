from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from uuid import uuid4
from time import strftime
import hashlib

from os.path import basename, dirname, exists, splitext, join
from os import makedirs, system
from shutil import rmtree, move, copyfile
import tarfile
import datetime

def mergedict(a, b):
	res = a.copy()
	try:
		for key, val in b.items():
			if key in res:
				res[key] += val
			else:
				res[key] = val
	except AttributeError:
		return NotImplemented
	return res

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

class Affiliation(models.Model):
	name = models.CharField(max_length = 50)
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

#The custom user class
class Individual(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	activation_token = models.UUIDField(primary_key=False, default=uuid4, editable=False)
	shortbio = models.TextField(editable=True, default="", blank=True)
	affiliations = models.ManyToManyField(Affiliation)
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.user.username)
	def save(self, *args, **kwargs):
		if not self.pk:
			try:
				p = Individual.objects.get(user=self.user)
				self.pk = p.pk
			except Individual.DoesNotExist:
				pass
		super(Individual, self).save(*args, **kwargs)
	def last_submission(self, competition):
		try:
			return self.submission_set.filter(subtrack__track__competition=competition).latest('timestamp').timestamp
		except:
			return None
		
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Individual.objects.get_or_create(user=instance)  

#TODO: Use the @receiver decorator here?
post_save.connect(create_user_profile, sender=User) 		

class Competition(models.Model):
	organizer = models.ManyToManyField(Individual)
	#The following control the individual's position on the organizer list
	# Leading_organizers show up higher than midtier_organizers and other organizers.
	# Midtier_orginazers show up higher than other (non-leading) organizers.
	leading_organizer = models.ManyToManyField(Individual, related_name='leading_organizer', blank=True)
	midtier_organizer = models.ManyToManyField(Individual, related_name='midtier_organizer', blank=True)
	watchers = models.ManyToManyField(Individual, related_name='watchers', blank=True)
	#
	name = models.CharField(max_length = 100)
	url_alias = models.SlugField(max_length = 30, editable=True, default="") #This is used for the URL shortcut (see urls.py, issue #72)
	avatar = models.FileField(upload_to='uploads/avatars/', null=True, blank=True)
	overview = models.TextField(editable=True, default="")
	newsfeed = models.TextField(editable=True, default="")
	important_dates = models.TextField(editable=True, default="")
	is_public = models.BooleanField(default=True)
	submission_is_open = models.BooleanField(default=True)
	force_private_submissions = models.BooleanField(default=True)
	force_undeletable_submissions = models.BooleanField(default=True)
	submission_restriction_in_minutes = models.IntegerField(default="20", blank=False, verbose_name="Time restriction (in minutes) between consecutive submissions (may be set to zero)")
	cc_email = models.EmailField(blank=True, verbose_name="An email will be sent here, everytime there is a submission")
	deadline_active = models.BooleanField(default=False)
	deadline = models.DateField(default=now)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

class Track(models.Model):
	percomp_uniqueid = models.IntegerField(default="1", blank=False) 
	name = models.CharField(max_length = 50)
	overview = models.TextField(editable=True, default="")
	competition = models.ForeignKey(Competition, on_delete = models.CASCADE)
	def __str__(self):
		return '({}) {}, part of {}'.format(self.id, self.name, self.competition.name)
	def uniqueid_isunique(self):
		conflict_list = self.competition.track_set.filter(percomp_uniqueid=self.percomp_uniqueid)
		for memb in conflict_list:
			if self.id != memb.id:
				return False
		return True
	def get_next_uniqueid(self):
		alltracks = self.competition.track_set.all()
		if not alltracks:
			return "1"
		next_uniqueid = int(alltracks[0].percomp_uniqueid)
		for t in alltracks:
			current_uniqueid = int(t.percomp_uniqueid)
			if current_uniqueid > next_uniqueid:
				next_uniqueid = current_uniqueid
		next_uniqueid += 1
		return(str(next_uniqueid))		
	def clean(self):
		try:
			if not self.uniqueid_isunique():
				self.percomp_uniqueid = self.get_next_uniqueid()			
		except AttributeError:
			raise ValidationError(
				_('You must specify all required fields.'),
				params={},
				)
	def save(self, *args, **kwargs):
		if not self.uniqueid_isunique():
			self.percomp_uniqueid = self.get_next_uniqueid()
		super(Track, self).save(*args, **kwargs)
	def scoretable(self):
		def create_board_row(idx, s, key, val):
			aff = set()
			for subm in s.submitter.all():
				for a in subm.affiliations.all():
					aff.add(a)
			newrow = {
				'position': idx,
				'name': key,
            	'method_info': s.method_info,
            	'submitter': ', '.join(['{} {}'.format(subm.user.first_name, subm.user.last_name) for subm in s.submitter.all()]),
   	        	'affiliation': ', '.join([a.name for a in aff]), 
				'before_deadline': s.before_deadline(),
				'score': val,
	        }
			return newrow
		res = []
		idx = 0
		data = {}
		after_deadline_list = []
		for s in self.subtrack_set.all():
			data = mergedict(data, s.scoretable())
		for (key, val) in sorted(data.items(), key = lambda s: s[1]):
			s = Submission.objects.filter(name=key)[0]
			if s.before_deadline():
				idx = idx+1
			else:
				after_deadline_list.append((s, key, val))
				continue
			res.append(create_board_row(idx, s, key, val))
		for (s, key, val) in after_deadline_list:
			res.append(create_board_row(None, s, key, val))
		return res

def publicdata_path(instance, filename):
	return 'databases/{}/{}'.format(uuid4().hex, filename)

def privatedata_path(instance, filename):
	return 'databases/{}/{}'.format(uuid4().hex, filename)

class Subtrack(models.Model):
	pertrack_uniqueid = models.IntegerField(default="1", blank=False)	
	name = models.CharField(max_length = 50)
	track = models.ForeignKey(Track, on_delete = models.CASCADE)
	#Public data link here via a foreign key relation
	#
	#This will be test folds, non-visible to participants, usable only by the evaluation system
	private_data = models.FileField(upload_to=privatedata_path, null=True) #Not sure if FileField is proper in this case
	#This hash is used to monitor user changes on private data
	private_data_securehash = models.CharField(max_length=100, null=True, blank=True, default="")
	def __str__(self):
		return '({}) {}, part of {} / {}'.format(self.id, self.name, self.track.competition.name, self.track.name)
	def uniqueid_isunique(self):
		conflict_list = self.track.subtrack_set.filter(pertrack_uniqueid=self.pertrack_uniqueid)
		for memb in conflict_list:
			if self.id != memb.id:
				return False
		return True
	def get_next_uniqueid(self):
		allsubtracks = self.track.subtrack_set.all()
		if not allsubtracks:
			return "1"
		next_uniqueid = int(allsubtracks[0].pertrack_uniqueid)
		for st in allsubtracks:
			current_uniqueid = int(st.pertrack_uniqueid)
			if current_uniqueid > next_uniqueid:
				next_uniqueid = current_uniqueid
		next_uniqueid += 1
		return(str(next_uniqueid))
	def clean(self):
		try:
			if not self.uniqueid_isunique():
				self.pertrack_uniqueid = self.get_next_uniqueid()			
		except AttributeError:
			raise ValidationError(
				_('You must specify all required fields.'),
				params={},
				)			
	def save(self, *args, **kwargs):
		dont_call_unpack_privatefolder = kwargs.pop('dont_call_unpack_privatefolder', False)
		if not dont_call_unpack_privatefolder:
			if not self.uniqueid_isunique():
				self.pertrack_uniqueid = self.get_next_uniqueid()
			#Call super_save once to save the file
			super(Subtrack, self).save(*args, **kwargs)
			self.unpack_privatefolder()
			#Call again super_save to save the new hash
			#self.save(justcall_super=True, *args, **kwargs)
		else:
			super(Subtrack, self).save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		super(Subtrack, self).delete(*args, **kwargs)
		self.delete_unpacked_privatefolder()

	def private_data_root_folder(self):
		return dirname(self.private_data.name)
	def private_data_unpacked_folder(self):
		return '{}/unpacked/'.format(self.private_data_root_folder())
	def save_privatedata_hash(self):
		# used code from http://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
		hash_md5 = hashlib.md5()
		with open(self.private_data.name, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
		self.private_data_securehash = hash_md5.hexdigest()
	def unpack_privatefolder(self):
		currenthash = self.private_data_securehash
		print(currenthash)
		self.save_privatedata_hash()
		newhash = self.private_data_securehash
		print(newhash)
		if(newhash != currenthash):
			print("Extracting")
			self.delete_unpacked_privatefolder()
			fn, fn_ext = splitext(basename(self.private_data.name))
			if(tarfile.is_tarfile(self.private_data.name)):
				tar = tarfile.open(self.private_data.name)
				tar.extractall(path=self.private_data_unpacked_folder())
				tar.close()			
			elif(fn_ext == '.7z'):
				if not exists(self.private_data_unpacked_folder()):
					makedirs(self.private_data_unpacked_folder())
				system('7zr x {} -o{}'.format(self.private_data.name, self.private_data_unpacked_folder()))
			else:
				#Don't know how to unzip this, so we'll just copy it
				if not exists(self.private_data_unpacked_folder()):
					makedirs(self.private_data_unpacked_folder())
				copyfile(
					self.private_data.name, 
					join(self.private_data_unpacked_folder(), basename(self.private_data.name))
				)
			print("Created folder on {}".format(self.private_data_unpacked_folder()))
			self.save(dont_call_unpack_privatefolder=True)
	def delete_unpacked_privatefolder(self):
		#TODO: (non-major?) unpacked folder wont be deleted if the user uploads a new private test file,
		#	as the securehash is changed and the old folder is 'lost'
		if self.private_data_securehash and exists(self.private_data_unpacked_folder()): 
			src = self.private_data_unpacked_folder()
			#TODO: Specify on settings.py or elsewhere the /tmp/ folder as a constant
			dst = '/tmp/{}'.format(uuid4().hex)			
			# rmtree(src)			
			print("Deleting unpacked dir {} (actually just moved to {})".format(src, dst))
			move(src, dst) #this is safer than rmtree.. !
	def scoretable(self):
		data = {}
		for b in self.benchmark_set.all():
			if(b in self.track.competition.count_in_scoreboard.all()):
				data = mergedict(data, b.scoretable(self.id))
		return data

def submission_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_.../<datestamp>/<random unique identifier>/filename
	return 'uploads/submitted_results/{}/{}/{}'.format(
		strftime("%Y_%m_%d"),
		uuid4().hex, 
		filename)

class PublicLink(models.Model):
	subtrack = models.ForeignKey(Subtrack, on_delete = models.CASCADE)
	legend = models.CharField(max_length = 150, null=False, blank=False, default="Download training data")
	#This will normally be training+validation folds, visible to any registered user
	downloadableFile = models.FileField(upload_to=publicdata_path, null=True, blank=True, default="")
	#Organizers have the option of using a URL field here, in case they want to serve the public data themselves. If this is non-blank, it overrides the other fields
	externalLink = models.URLField(null=True, blank=True, default="")
	#TODO: Add sth here to cover showing thumbnails of training data (issue #3)
	def __str__(self):
		return '({}) {}'.format(self.legend, self.subtrack)	

class Submission(models.Model):
	name = models.SlugField(max_length = 20, null=False, blank=False, default="")
	method_info = models.TextField(editable=True, default="")
	publishable = models.BooleanField(default=True)
	submitter = models.ManyToManyField(Individual)
	subtrack = models.ForeignKey(Subtrack, on_delete = models.CASCADE, null=True)
	timestamp = models.DateTimeField(auto_now_add=True, null=True)
	resultfile = models.FileField(upload_to=submission_path, null=True) #Nullable because migrations complained, but it shouldnt ever be null
	def __str__(self):
		submitter_str = '';
		for k in self.submitter.all():
			submitter_str += k.user.username + ' '
		return '[{}/{}/{}/{}] ({}/{}) [{}] [{}...] [{}/{}/{}]'.format(
			submitter_str,
			self.subtrack.track.competition.id,			
			self.subtrack.track.percomp_uniqueid,
			self.subtrack.pertrack_uniqueid,
			self.id,
			self.name, 
			self.timestamp, 
			self.method_info[0:40],
			self.subtrack.track.competition.name[0:20],
			self.subtrack.track.name[0:20],
			self.subtrack.name[0:20]
		)
	def before_deadline(self):
		if not self.subtrack.track.competition.deadline_active:
			return True
		return self.timestamp.date() <= self.subtrack.track.competition.deadline

class EvaluatorFunction(models.Model):
	# The name of the callable 'evaluator' function is identical to the 'name' field of this model
	# The function itself is (has to be) found in the 'evaluators.py' file.
	name = models.SlugField(max_length = 50, null=False, blank=False, default="")
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)

class Benchmark(models.Model):
	# The evaluator_function returns a dictionary; the result for this benchmark is found
	# in the entry with key 'name'
	name = models.CharField(max_length = 50, null=False, blank=False, default="")
	evaluator_function = models.ForeignKey(EvaluatorFunction, on_delete = models.CASCADE, null=True)
	benchmark_info = models.TextField(editable=True, default="")
	subtracks = models.ManyToManyField(Subtrack, blank=True)
	count_in_scoreboard = models.ManyToManyField(Competition, blank=True, related_name="count_in_scoreboard")
	is_scalar = models.BooleanField(default=True)
	higher_is_better = models.BooleanField(default=True)
	def __str__(self):
		return '({}) {}'.format(self.id, self.name)
	def scoretable(self, subtrack_id):
		# Compute scores for this benchmark and the given subtrack
		res = {}
		subtrack = Subtrack.objects.get(pk=subtrack_id)
		for submission in subtrack.submission_set.all():
			if not submission.publishable:
				continue
			submission_status_all = SubmissionStatus.objects.filter(submission_id=submission.id).filter(benchmark_id=self.id)
			if not submission_status_all:
				continue;
			submission_status = submission_status_all.all()[0]			
			if submission_status.numericalresult and submission_status.status == 'COMPLETE':
				res[submission.name] = float(submission_status.numericalresult)
		sortedindices = argsort([ ((-1)**int(self.higher_is_better))*s for s in list(res.values()) ])
		ranks = [0]*len(sortedindices)
		for r in range(len(sortedindices)):
			ranks[sortedindices[r]] = r+1
		data = dict(zip(res.keys(), ranks))
		return data


class SubmissionStatus(models.Model):
	class Meta:
		verbose_name_plural = 'submission status'
	POSSIBLE_STATUS = (
		('UNDEFINED', _('The processing state of the submission is undefined')),
		('PROCESSING', _('We are currently processing the submitted result')),		
		('ERROR_EVALUATOR', _('Could not call the related evaluator function')),
		('ERROR_GENERIC', _('An error has occured before processing could start')),
		('ERROR_PROCESSING', _('An error has occured during processing of the submitted result')),
		('ERROR_UNSUPPORTED', _('This benchmark cannot be computed by the specified evaluator function')),
		('COMPLETE', _('The submitted result has been succesfully processed and a numerical result has been saved'))
	)
	submission = models.ForeignKey(Submission, on_delete = models.CASCADE, null=True)
	benchmark = models.ForeignKey(Benchmark, on_delete = models.CASCADE, null=True)
	numericalresult = models.CharField(max_length = 100, null=False, blank=False, default="")
	status = models.CharField(max_length = 20, choices=POSSIBLE_STATUS, default='UNDEFINED')
	start_time = models.DateTimeField(auto_now_add=True, null=True)
	end_time = models.DateTimeField(auto_now=True, null=True)
	def __str__(self):
		return '({}/{}) [score={}] [{}]'.format(self.benchmark, self.id, self.numericalresult, self.status)