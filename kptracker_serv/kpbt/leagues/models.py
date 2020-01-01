from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from kpbt.accounts.models import BowlerProfile
from kpbt.centers.models import BowlingCenter
from kpbt.teams.models import Team, TeamRoster
from kpbt.games.models import Series
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files import File
from kptracker.settings import SCHEDULEFILES_FOLDER as SCHEDULEDIR
from kptracker.settings import BACKUPS_FOLDER as BACKUPSDIR


from collections import deque
from itertools import islice
from dateutil import rrule
import datetime
import itertools
from num2words import num2words

import math, json

class League(models.Model):
	
	bowling_center = models.ForeignKey('BowlingCenter', on_delete=models.SET_NULL, null=True,
		related_name='leagues', verbose_name=('bowling center'))
	bowlers = models.ManyToManyField('BowlerProfile', through='LeagueBowler')
	
	secretary = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
	
	name = models.CharField(max_length=32)
	current_week = models.PositiveSmallIntegerField(default=1)
	week_pointer = models.PositiveSmallIntegerField(default=1)
	
	
	def __str__(self):
		return self.bowling_center.name + ", " + self.name
		
	def set_center(self, center_name):
		center = get_object_or_404(BowlingCenter, name=center_name)
		self.bowling_center = center
	
	def set_name(self, name):
		self.name = name
		
	def set_secretary(self, user):
		self.secretary = user
		self.save()
		
	
	def create_pairings(self):
		num_teams = self.leaguerules.num_teams
		num_weeks = self.schedule.num_weeks # // 2
		
		if num_teams % 2:
			num_teams += 1
			
		filename = str(num_teams) + 'teams'
		filedir = SCHEDULEDIR + filename + '.csv'
		
		pairings = [None] * num_weeks
		with open(filedir) as schedule:
			
			schedule.readline() #skip first line to allow week number to align with list index
			
			raw_weekly_pairings = schedule.readlines()
			week_number_counter=1
			for raw_pairings in raw_weekly_pairings:

				weekly_pairing_list = raw_pairings.strip('\n').split(',')
				
				pair_counter = 1
				for pair in weekly_pairing_list:
					
					teams = pair.split('-')
					team_one = Team.objects.get(league=self, number=teams[0])
					team_two = Team.objects.get(league=self, number=teams[1])
					new_pairing = WeeklyPairings.objects.create(league=self, team_one=team_one, team_two=team_two, week_number=week_number_counter, lane_pair = math.ceil(pair_counter))
					
					new_pairing.save()
					pair_counter +=1
				
				week_number_counter += 1
		

	def rescore(self, rescore_week):
		cw = self.current_week
		rules = self.leaguerules
		
		#1. Reload league from earlier backup to prepare for rescoring effort
		reset_week = rescore_week - 1
		print('reset week: ', reset_week)
		self.reset_weekly_from_backup(reset_week)
		
		#2. For ever week between reset_week and current week
		#	a. Reset series team points values to 0
		#	b. recalculate the applied average/handicap for that series
		#	c. Call score_league for that week after resetting
		
		for i in range (rescore_week, cw):
			series_data = Series.objects.filter(league=self, week_number=i)
			
			#Delete week's results records
			WeeklyResults.objects.filter(league=self, week_number=i).delete()
			
			for series in series_data:
				#Recalculate league_average and handicap values
				lb = get_object_or_404(LeagueBowler, league=self, bowler=series.bowler.id)
				
				if self.week_pointer == 1:
					average = lb.league_average
				else:
					average = lb.calc_average()
				if rules.is_handicap:
					handicap = (rules.handicap_percentage / 100) * (rules.handicap_scratch - average)
					if handicap < 0:
						handicap = 0
				else:
					handicap = 0
				
				series.applied_average = average
				series.applied_handicap = handicap
				series.save()
			self.score_week(i)

	
	def reset_weekly_from_backup(self, reset_week):
		backup_filename= str(self.id) + '_' + str(reset_week) + '.json'
		with open(BACKUPSDIR + backup_filename, 'r') as bkup:
			backup = json.load(bkup)
		
		for teams in backup['teams'].items():
			team = get_object_or_404(Team, league=self, number=teams[0])
			for key,value in teams[1].items():
				setattr(team, key, value)
				team.save()
		
		for lb_records in backup['league_bowler_records'].items():
			lb_record = get_object_or_404(LeagueBowler, league=self, id=lb_records[0])
			for key, value in lb_records[1].items():
				setattr(lb_record, key, value)
				lb_record.save()
		
		for tr_records in backup['team_roster_records'].items():
			tr = get_object_or_404(TeamRoster, id=tr_records[0])
			for key, value in tr_records[1].items():
				setattr(tr, key, value)
				tr.save()
		
		
	def score_week(self, week_number): 
		this_week = WeeklyPairings.objects.filter(league=self, week_number=week_number).order_by('lane_pair')
		rules = self.leaguerules
		
		for pair in this_week:
			team_one = pair.team_one
			team_two = pair.team_two
			
			results_one = WeeklyResults.objects.create(league=self, team=team_one, week_number=week_number, lane_pair=pair.lane_pair, opponent=team_two)
			results_two = WeeklyResults.objects.create(league=self, team=team_two, week_number=week_number, lane_pair=pair.lane_pair, opponent=team_one)
			
			results_one.opponent = team_two
			results_two.opponent = team_one
			
			team_one_series = Series.objects.filter(league=self, team=team_one, week_number=week_number)
			team_two_series = Series.objects.filter(league=self, team=team_two, week_number=week_number)
			
			game_points = rules.game_point_value
			series_points = rules.series_point_value
			weekly_points = rules.total_weekly_points()
			
			team_one_total_series = 0
			team_two_total_series = 0
			
			team_one_points = 0
			team_two_points = 0
			
			for i in range(1, 4): #Games number 1-3
				game = 'g' + str(i)
				
				t1_hc_score = Series.calc_team_handicap_game_score(team_one, week_number, i, team_one_series)
				setattr(results_one, game, t1_hc_score)
				team_one_total_series += t1_hc_score
				t2_hc_score = Series.calc_team_handicap_game_score(team_two, week_number, i, team_two_series)
				setattr(results_two, game, t2_hc_score)
				team_two_total_series += t2_hc_score
				
				if t1_hc_score > t2_hc_score:
					team_one_points += game_points
				elif t1_hc_score < t2_hc_score:
					team_two_points += game_points
				else:
					team_one_points += game_points / 2
					team_two_points += game_points / 2
			
			results_one.series = team_one_total_series
			results_two.series = team_two_total_series
			
			if team_one_total_series > team_two_total_series:
				team_one_points += series_points
			elif team_one_total_series < team_two_total_series:
				team_two_points += series_points
			
			results_one.points_won = team_one_points
			results_one.points_lost = weekly_points - team_one_points
			
			results_two.points_won = team_two_points
			results_two.points_lost = weekly_points - team_two_points

			results_one.save()
			results_two.save()
			
			team_one.update_points(team_one_points, weekly_points - team_one_points)
			team_two.update_points(team_two_points, weekly_points - team_two_points)
			
			team_one.update_team_pinfall(team_one_series)
			team_two.update_team_pinfall(team_two_series)
			
			for series1 in team_one_series:
				lb_record = get_object_or_404(LeagueBowler, league=self, bowler= series1.bowler)
				lb_record.update(series1)
				
				tr_record = get_object_or_404(TeamRoster, bowler=series1.bowler, team=series1.team)
				tr_record.update_games(series1)
			
			for series2 in team_two_series:
				lb_record = get_object_or_404(LeagueBowler, league=self, bowler= series2.bowler)
				lb_record.update(series2)
				
				tr_record = get_object_or_404(TeamRoster, bowler=series2.bowler, team=series2.team)
				tr_record.update_games(series2)


	def create_weekly_score_backup(self, week_number):
		#week_number = self.week_pointer
		backup_filename= str(self.id) + '_' + str(week_number) + '.json'
		
		backup = open(BACKUPSDIR + backup_filename, 'w') 
		backup_dict = {}
		
		
		#Backups file header information
		header_dict = { "league_name": self.name , "week" : str(week_number) } 
		backup_dict.update( {"header" : header_dict})
		
		
		#Teams Backup Info
		teams_set = self.teams.all()
		teams = {}
		for team in teams_set:
			team_dict = {team.id :  {"total_scratch_pins" : team.total_scratch_pins, "total_handicap_pins": team.total_handicap_pins, "total_pinfall" : team.total_pinfall, "team_points_won" : team.team_points_won, "team_points_lost" : team.team_points_lost}}
		
			teams.update(team_dict)
		backup_dict.update({"teams" : teams})
		
		
		#LeagueBowler/TeamRoster Backups
		lb_records = LeagueBowler.objects.filter(league=self)
		tr_records = TeamRoster.objects.filter(team_id__in=teams)
		
		team_rosters_dict = {}
		lb_records_dict = {}
		
		for lb in lb_records:
			lb_dict = {lb.id : {"league_average" : lb.league_average, "games_bowled" : lb.games_bowled, "league_total_scratch" : lb.league_total_scratch, "league_total_handicap" : lb.league_total_handicap, "league_high_scratch_game" : lb.league_high_scratch_game, "league_high_handicap_game" : lb.league_high_handicap_game, "league_high_scratch_series" : lb.league_high_scratch_series, "league_high_handicap_series" : lb.league_high_handicap_series} }
			lb_records_dict.update(lb_dict)
		backup_dict.update({"league_bowler_records" : lb_records_dict})
		
		
		for tr in tr_records:
			tr_dict = {tr.id : { "games_with_team" : tr.games_with_team }}
			team_rosters_dict.update(tr_dict)
		backup_dict.update({"team_roster_records" : team_rosters_dict})
		
		json.dump(backup_dict, backup, indent=4)
		
		with open(BACKUPSDIR + backup_filename) as backup:
			data = json.load(backup)
		backup.close()
		
	def advance_week(self):
		self.current_week += 1
		self.week_pointer = self.current_week
		
	def set_week_pointer(self, week_selection):
		self.week_pointer = week_selection
		
class LeagueRules(models.Model):
	league = models.OneToOneField(League, on_delete=models.CASCADE)
	
	DESIGNATION = (
		('A', 'Adult'),
		('S', 'Senior'),
		('J', 'Junior'),
		('N', 'Any'),
	)
	
	GENDER = (
		('M', 'Men'),
		('W', 'Women'),
		('X', 'Mixed'),
	)
	
	num_teams = models.PositiveSmallIntegerField()
	designation = models.CharField(max_length=1, choices=DESIGNATION)
	gender = models.CharField(max_length=1, choices=GENDER)
	playing_strength = models.PositiveSmallIntegerField(default=1)
	max_roster_size = models.PositiveSmallIntegerField(default=9)
	entering_average = models.PositiveSmallIntegerField(default=0)
	is_handicap = models.BooleanField(default=False)
	handicap_scratch = models.PositiveSmallIntegerField(default=0)
	handicap_percentage = models.PositiveSmallIntegerField(default=0)

	bye_team_point_threshold = models.PositiveSmallIntegerField(default=0)
	absentee_score = models.PositiveSmallIntegerField(default=0)
	game_point_value = models.PositiveSmallIntegerField(default=0)
	series_point_value = models.PositiveSmallIntegerField(default=0)

	def total_weekly_points(self):
		return (3 * self.game_point_value) + self.series_point_value

class LeagueBowler(models.Model):
	bowler = models.ForeignKey(BowlerProfile, on_delete=models.CASCADE)
	league = models.ForeignKey(League, on_delete=models.CASCADE)
	
	games_bowled = models.PositiveSmallIntegerField(default=0)
	league_average = models.PositiveSmallIntegerField(default=0)
	league_high_scratch_game = models.PositiveSmallIntegerField(default=0)
	league_high_handicap_game = models.PositiveSmallIntegerField(default=0)
	league_high_scratch_series = models.PositiveSmallIntegerField(default=0)
	league_high_handicap_series = models.PositiveSmallIntegerField(default=0)
	league_total_scratch = models.PositiveSmallIntegerField(default=0)
	league_total_handicap = models.PositiveSmallIntegerField(default=0)
	
	def __str__(self):
		return self.bowler.get_name()
	
	
	def update(self, series):
		series_scratch_score = 0
		series_handicap_score = 0
		games_played_counter = 0
		
		handicap = series.applied_handicap
		average = series.applied_average
		#if not scores:
			#scores = Series.objects.filter(league=self.league, bowler=self.bowler, week_number=self.league.week_pointer)
		scores = series.get_scores_list()
		
		for score in scores:
			if score[0] == 'A':
				#Bowler was absent for this game, does not count toward league stats
				pass
			else:
				games_played_counter += 1
				series_scratch_score += int(score)
				if int(score) > self.league_high_scratch_game: #Update highest scratch score
					self.league_high_scratch_game = int(score)
				
				
				game_handicap_score = int(score) + int(handicap)
				series_handicap_score += game_handicap_score
				if game_handicap_score > self.league_high_handicap_game: #Update highest handicap game score
					self.league_high_handicap_game = game_handicap_score

		self.games_bowled += games_played_counter
		
		self.league_total_scratch += series_scratch_score
		if series_scratch_score > self.league_high_scratch_series:
			self.league_high_scratch_series = series_scratch_score
			
		self.league_total_handicap += series_handicap_score
		if series_handicap_score > self.league_high_handicap_series:
			self.league_high_handicap_series = series_handicap_score
	

		self.update_average()
		self.save()
	
	def update_average(self):
		self.league_average = self.league_total_scratch / self.games_bowled
	
	def calc_average(self):
		return self.league_total_scratch / self.games_bowled
		
class Schedule(models.Model):
	WEEKDAY = (
		('MO', 'Monday'),
		('TU', 'Tuesday'),
		('WE', 'Wednesday'),
		('TH', 'Thursday'),
		('FR', 'Friday'),
		('SA', 'Saturday'),
		('SU', 'Sunday'),
	)
	
	league = models.OneToOneField(League, on_delete=models.CASCADE)

	date_starting = models.DateField()
	date_ending = models.DateField()
	num_weeks = models.PositiveSmallIntegerField(default=0)
	start_time = models.TimeField()
	
	day_of_week = models.CharField(max_length=2, choices=WEEKDAY)
	
	
	def calc_num_weeks(self):
		weeks = rrule.rrule(rrule.WEEKLY, dtstart=self.date_starting, until=self.date_ending)
		self.num_weeks = weeks.count()
	
class WeeklyResults(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='results')
	
	week_number = models.PositiveSmallIntegerField(default=0)
	lane_pair = models.PositiveSmallIntegerField(default=0)
	
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	opponent = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='opponent')
	
	average = models.PositiveSmallIntegerField(default=0)
	handicap = models.PositiveSmallIntegerField(default=0)
	
	g1 = models.PositiveSmallIntegerField(default=0)
	g2 = models.PositiveSmallIntegerField(default=0)
	g3 = models.PositiveSmallIntegerField(default=0)
	series = models.PositiveSmallIntegerField(default=0)
	points_won = models.PositiveSmallIntegerField(default=0)
	points_lost = models.PositiveSmallIntegerField(default=0)
		

class WeeklyPairings(models.Model):
	league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='pairings')
	
	team_one = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='first_pair')
	team_two = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='second_pair')
	
	week_number = models.PositiveSmallIntegerField(default=0)
	lane_pair = models.PositiveSmallIntegerField(default=0)
	
	def __str__(self):
		return str(self.team_one.number) + " - " + str(self.team_two.number)
		
		
	def get_lanes_by_pairnumber(self):
		return str(self.lane_pair *2 - 1) + ' - ' + str(self.lane_pair*2)
