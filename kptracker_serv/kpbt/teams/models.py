from django.db import models
#from kpbt.leagues.models import League
from kpbt.accounts.models import BowlerProfile
from django.contrib.auth.models import User

from num2words import num2words

class Team(models.Model):
	
	league = models.ForeignKey('League', on_delete=models.CASCADE,
		related_name = 'teams', verbose_name = 'league')
	
	number = models.PositiveSmallIntegerField()
	name = models.CharField(max_length=32, default="")
	total_pinfall = models.PositiveSmallIntegerField(default=0)
	total_handicap_pins = models.PositiveIntegerField(default=0)
	total_scratch_pins = models.PositiveIntegerField(default=0)
	team_points_won = models.PositiveSmallIntegerField(default=0)
	team_points_lost = models.PositiveIntegerField(default=0)
	
	roster = models.ManyToManyField(BowlerProfile, through='TeamRoster')
	
	def update_points(self, points_won, points_lost):
		self.team_points_won += points_won
		self.team_points_lost += points_lost
		self.save()
	
	
	def update_team_pinfall(self, series_list):
		for series in series_list:
			scratch_score = 0
			handicap_score = 0
		
			scores = series.get_scores_list()
			handicap = series.applied_handicap
			
			for score in scores:
				if score[0] == 'A':
					scratch_score += int(score[1:])
				else:
					scratch_score += int(score)
					handicap_score += int(handicap)
				
			self.total_scratch_pins += scratch_score
			
			print(self.name, ': ', self.total_scratch_pins)
			
			self.total_handicap_pins += handicap_score
			print(self.name, ': ', self.total_handicap_pins)
			self.total_pinfall += scratch_score + handicap_score
		self.save()
		
	def create_team(league, number):
		new_team = Team(league=league, number=number,
			name='Team' + num2words(number))
		return new_team
		
	def __str__(self):
		return self.name
		
		
class TeamRoster(models.Model):
	bowler = models.ForeignKey('BowlerProfile', on_delete=models.CASCADE, related_name='roster_record')
	team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='roster_record')
	games_with_team = models.PositiveSmallIntegerField(default=0)
	
	is_active = models.BooleanField(default=True)
	lineup_position = models.PositiveSmallIntegerField(default=0)
	
	
	def __str__(self):
		return self.bowler.first_name + " " + self.bowler.last_name + ", " + self.team.name
	
	def get_bowler(self):
		return self.bowler
	
	def create_roster_record(team, bowler):
		roster_record = TeamRoster(bowler=bowler, team=team)
		return roster_record
	
	def swap_roster_spots(self, roster_record):
		if self.team is roster_record.team:
			swap = roster_record.lineup_position
			roster_record.lineup_position = self.lineup_position
			self.lineup_position = swap
	
	def set_lineup_position(self, position):
		self.lineup_position = position
	
	def update_games(self, series):
		counter = 0
		
		game_scores = series.get_scores_list()
		for score in game_scores:
			if score[0] is 'A':
				pass
			else:
				counter += 1
		self.games_with_team += counter
		self.save()
		