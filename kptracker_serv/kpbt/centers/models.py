from django.db import models
from django.contrib.auth.models import User

class BowlingCenter(models.Model):
	name = models.CharField(max_length = 64, unique=True)
	num_lanes = models.IntegerField(default=0, verbose_name='number of lanes')
	
	manager= models.OneToOneField(User, on_delete=models.SET_NULL, null=True,
		related_name='center_managed', verbose_name=('manager'))
	
	def __str__(self):
		return self.name
		
	def set_manager(self, user):
		self.manager = user
	
	def get_address(self):	
		return self.centeraddress
		
class CenterAddress(models.Model):
	STATES = (
		('AL', 'Alabama'),
		('AK', 'Alaska'),
		('AZ', 'Arizona'),
		('AR', 'Arkansas'),
		('CA', 'California'),
		('CO', 'Colorado'),
		('CT', 'Conneticut'),
		('DE', 'Deleware'),
		('DC', 'District of Columbia'),
		('FL', 'Florida'),
		('GA', 'Georgia'),
		('HA', 'Hawaii'),
		('ID', 'Idaho'),
		('IL', 'Illinois'),
		('IN', 'Indiana'),
		('IA', 'Iowa'),
		('KS', 'Kansas'),
		('KY', 'Kentucky'),
		('LA', 'Louisiana'),
		('ME', 'Maine'),
		('MD', 'Maryland'),
		('MA', 'Massachusetts'),
		('MI', 'Michigan'),
		('MN', 'Minnesota'),
		('MS', 'Mississippi'),
		('MO', 'Missouri'),
		('MT', 'Montana'),
		('NE', 'Nebraska'),
		('NV', 'Nevada'),
		('NH', 'New Hampshire'),
		('NJ', 'New Jersey'),
		('NM', 'New Mexico'),
		('NY', 'New York'),
		('NC', 'North Carolina'),
		('ND', 'North Dakota'),
		('OH', 'Ohio'),
		('OK', 'Oklahoma'),
		('OR', 'Oregon'),
		('PA', 'Pennsylvania'),
		('RI', 'Rhode Island'),
		('SC', 'South Carolina'),
		('SD', 'South Dakota'),
		('TN', 'Tennessee'),
		('TX', 'Texas'),
		('UT', 'Utah'),
		('VT', 'Vermont'),
		('VA', 'Virginia'),
		('WA', 'Washington'),
		('WV', 'West Virgina'),
		('WI', 'Wisconsin'),
		('WY', 'Wyoming'),
	)
	
	bowling_center = models.OneToOneField(BowlingCenter, on_delete=models.CASCADE, related_name="address")
	
	street_addr = models.CharField(max_length=64)
	city = models.CharField(max_length=64)
	state = models.CharField(max_length=2, choices=STATES)
	zip_code = models.CharField(max_length=10)
	
	
	def __str__(self):
		return self.street_addr +' ' + self.city + self.state + ', ' + self.zip_code
			