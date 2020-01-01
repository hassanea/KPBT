from django.db import models
from django.contrib.auth.models import User
import datetime

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='userprofile')
	email = models.EmailField(
		verbose_name='email address',
		max_length = 254,
		unique = False,
	)
	
	is_bowler = models.BooleanField(default=False)
	is_league_secretary = models.BooleanField(default=False)
	is_center_manager = models.BooleanField(default=False)
	
	def __str__(self):
		return self.first_name + ' ' + self.last_name
	
	def set_center_manager(self, is_manager):
		self.is_center_manager = is_manager
	
	def set_league_secretary(self, is_league_secretary):
		self.is_league_secretary = is_league_secretary


	
class BowlerProfile(models.Model):
	HAND = (
		('R', 'Right'),
		('L', 'Left')
	)

	DESIGNATION = (
		('A', 'Adult'),
		('S', 'Senior'),
		('J', 'Junior')
	)
	
	GENDER = (
		('M', 'Male'),
		('F', 'Female'),
	)
	
	user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
	
	first_name = models.CharField(max_length=64, blank=True)
	last_name = models.CharField(max_length=64, blank=True)
	
	hand = models.CharField(max_length=1, choices=HAND, blank=True)
	designation = models.CharField(max_length=1, choices=DESIGNATION, blank=True)
	gender = models.CharField(max_length=1, choices=GENDER, blank=True)
	
	is_linked = models.BooleanField(default=False)
		
	def __str__(self):
		return self.first_name + ' ' + self.last_name		
		
	def create_empty_profile():
		return BowlerProfile()
		
	def get_name(self):
		return self.first_name + ' ' + self.last_name
		
		
class Links(models.Model):
	TYPES = (
		('C', 'Bowling Center'),
		('L', 'League'),
		('T', 'Team'),
		('B', 'Bowler'),
	)
	
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	type = models.CharField(max_length=1, choices=TYPES)
	type_id = models.PositiveSmallIntegerField()
		