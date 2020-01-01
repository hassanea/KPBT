from django.db import models
from kpbt.accounts.models import BowlerProfile
from kpbt.teams.models import Team

from num2words import num2words

class Series(models.Model):
	bowler = models.ForeignKey(BowlerProfile, on_delete=models.SET_NULL, null=True)
	team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True)
	league = models.ForeignKey('League', on_delete=models.SET_NULL, null=True)

	series_date = models.DateField(default='1900-01-01')
	week_number = models.PositiveSmallIntegerField(default=0)
	pair_number = models.PositiveSmallIntegerField(default=0)
	applied_average = models.PositiveSmallIntegerField(default=0)
	applied_handicap = models.PositiveSmallIntegerField(default=0)
	game_one_score = models.CharField(max_length=4, blank=True)
	game_two_score = models.CharField(max_length=4, blank=True)
	game_three_score = models.CharField(max_length=4, blank=True)
	scratch_score = models.IntegerField(default=0)
	handicap_score = models.IntegerField(default=0)

	def __str__(self):
		return self.bowler.get_name() + ', ' + str(self.applied_average) + ', ' + str(self.applied_handicap) + ', ' + str(self.game_one_score) + ', ' + str(self.game_two_score) + ', ' + str(self.game_three_score)
	
	def get_bowler_name(self):
		return self.bowler.get_name()
	
	def get_scratch_score(self):
		scratch_score = 0
		for score in [self.game_one_score, self.game_two_score, self.game_three_score]:
			if score[0] == 'A':
				pass
			else:
				scratch_score += int(score)
		return scratch_score
			
	def get_handicap_score(self):
		handicap_score = 0
		for score in [self.game_one_score, self.game_two_score, self.game_three_score]:
			if score[0] == 'A':
				pass
			else:
				handicap_score += int(score) + self.applied_handicap
		return handicap_score
	
	def set_points_won(self, points):
		self.weekly_points_won = points
		self.team.team_points_won += points
		
	def set_points_lost(self, points):
		self.weekly_points_lost = points
		self.team.team_points_lost += points
		
	def reset_points(self):
		self.weekly_points_won = 0
		self.weekly_points_lost = 0
	
	
	def get_scores_list(self):
		scores = []
		scores.append(self.game_one_score)
		scores.append(self.game_two_score)
		scores.append(self.game_three_score)
		return scores
	
	@staticmethod	
	def calc_team_handicap_game_score(team, week_number, game_number, team_series):
		handicap_score = 0
		
		for game in team_series:
			gamefield = 'game_' + num2words(game_number) +'_score'
			handicap_score += int(getattr(game, gamefield)) + int(game.applied_handicap)
		
		return handicap_score
			
	@staticmethod
	def calc_team_scratch_game_score(team, week_number, game_number, team_series):
		scratch_score = 0
		
		for game in team_series:
			gamefield = 'game_' + num2words(game_number) +'_score'
			scratch_score += int(getattr(game, gamefield))
			
		return scratch_score