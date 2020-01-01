from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from kpbt.leagues.forms import LeagueCreationForm, CreateScheduleForm, UpdateLeagueSecretaryForm, UpdateLeagueRulesForm, UpdateScheduleForm, RenameLeagueForm, MoveLeagueForm, SetWeekForm
from kpbt.leagues.forms import WeeklyPairingsForm, WeeklyPairingsFormSet, RestartLeagueForm
from kpbt.accounts.models import BowlerProfile
from kpbt.leagues.models import League, LeagueBowler, WeeklyPairings, WeeklyResults
from kpbt.centers.models import BowlingCenter
from kpbt.teams.models import Team, TeamRoster
from kpbt.games.models import Series
from kptracker.settings import ROSTEREXPORT_FOLDER as ROSTERS_DIR
from kpbt.games.forms import ImportScoresForm, EditScoresForm
from kptracker.settings import SCOREFILES_FOLDER as SCOREDIR
from kptracker.settings import BACKUPS_FOLDER as BACKUPSDIR
from django.forms import modelformset_factory, formset_factory
from django.core.paginator import Paginator
import math, json


def auth_test(request, league=""):
	if request.user.is_superuser:
		return True
	elif league.secretary == request.user:
		return True
	else:
		return False


def create_league(request, center_name=""):
	center = get_object_or_404(BowlingCenter, name=center_name)
	print(center.manager)
	print(request.user)
	print(request.user == center.manager or request.user.is_superuser)
	if not(request.user.is_superuser or request.user == center.manager):
		print('false')
		return redirect('center-home')
	
	if request.method == 'POST':
		center = get_object_or_404(BowlingCenter, name=center_name)
		
		schedule_form = CreateScheduleForm(request.POST)
		league_form = LeagueCreationForm(request.POST)
		if schedule_form.is_valid() and league_form.is_valid():
			new_league = League.objects.create(
				name=league_form.cleaned_data['league_name'], bowling_center=center,)
			new_league.save()
			
			#create and save league schedule
			schedule = schedule_form.save(commit=False)
			schedule.league = new_league
			schedule.calc_num_weeks()
			
			#create and save league rules
			leaguerules = league_form.save(commit=False)
			leaguerules.league = new_league
		
			#create base empty teams with empty rosters for league
			roster_size = leaguerules.playing_strength
			for i in range(1,league_form.cleaned_data['num_teams'] +1 ):
				teami = Team.create_team(new_league, i)
				teami.save()	
			
			#generate weekly lane pairings
			new_league.create_pairings()
			
			
			#save models
			schedule.save()
			leaguerules.save()
			return redirect('center-home', center_name=center_name)
		else:
			print(schedule_form.errors)
			print(league_form.errors)
	else:
		schedule_form = CreateScheduleForm()
		league_form = LeagueCreationForm()
	return render(request, 'leagues/manage/create_league.html', {'schedule_form' : schedule_form, 'league_form' : league_form })


def update_league(request, center_name="", league_name=""):
	
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	schedule = league.schedule
	rules = league.leaguerules
	
	if request.method == 'POST':
		name_form = RenameLeagueForm(request.POST, instance=league)
		rules_form = UpdateLeagueRulesForm(request.POST, instance=rules)
		schedule_form = UpdateScheduleForm(request.POST, instance=schedule)
		
		if name_form.is_valid() and rules_form.is_valid() and schedule_form.is_valid():
			updated_name = name_form.save(commit=False)
			updated_rules = rules_form.save(commit=False)
			updated_schedule = schedule_form.save(commit=False)
			
			updated_rules.league = league
			updated_schedule.league= league
			
			updated_name.save()
			updated_schedule.save()
			updated_rules.save()
			
			return redirect('update-league', league.bowling_center.name, league.name)
	
	else:
		name_form = RenameLeagueForm(instance=league)
		rules_form = UpdateLeagueRulesForm(instance=rules)
		schedule_form = UpdateScheduleForm(instance=schedule)
	return render(request, 'leagues/manage/update_league.html', {'name_form' : name_form, 'rules_form' : rules_form, 'schedule_form' : schedule_form})


def view_league(request, center_name = "", league_name=""):
	if center_name:
		if league_name:
			center = get_object_or_404(BowlingCenter, name=center_name)
			league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
			
			
			rulesform = LeagueCreationForm(instance = league.leaguerules)
			scheduleform = CreateScheduleForm(instance = league.schedule)
			
			weekly_pairings = WeeklyPairings.objects.filter(league=league, week_number=league.week_pointer)
			teams = league.teams.all().order_by('-team_points_won')
			bowlers = LeagueBowler.objects.filter(league__name=league_name).exclude(bowler__id=0)
			
			paginator = Paginator(bowlers, 25) # show 25 bowlers per page
			page = request.GET.get('page')
			league_bowlers = paginator.get_page(page)
			
			
			last_week_scores=[]
			secretary = league.secretary
			
			league_standings = {}
			if league.week_pointer > 1:
				last_week = league.week_pointer - 1
				results = WeeklyResults.objects.filter(league=league, week_number=last_week).order_by('lane_pair')
			else:
				results = {}
				
			return render(request, 'leagues/view_league.html', 
				{'league' : league, 'rules' : rulesform, 'schedule': scheduleform, 'teams' : teams, 'weekly_pairings' : weekly_pairings, 'bowlers' : league_bowlers, 'last_week' : last_week_scores,
					'secretary' : secretary, 'results' : results})
		else:
			center = get_object_or_404(BowlingCenter, name=center_name)
			leagues = center.leagues.all()
			return render(request, 'centers/view_center.html', {'leagues' : leagues, 'center' : center })
	else:
		leagues = League.objects.all()
		return render(request, 'leagues/league_home.html', {'leagues' : leagues})


def view_schedule(request, center_name="", league_name=""):
	
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	weekly_schedule = []
	schedule = WeeklyPairings.objects.filter(league=league).order_by('week_number')
	
	for i in range(1, league.schedule.num_weeks):
		week_pairs = WeeklyPairings.objects.filter(league=league, week_number=i)
		if week_pairs:
			week_list = []
			for pair in week_pairs:
				teams = str(pair)
				week_list.append(teams)
			weekly_schedule.append(week_list)
	
	return render(request, 'leagues/view_schedule.html', {'league' : league, 'schedule' : weekly_schedule })


def view_league_bowler(request, center_name="", league_name="", bowler_id=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	l_bowler = get_object_or_404(LeagueBowler, id=bowler_id)
	profile = get_object_or_404(BowlerProfile, id=l_bowler.bowler.id)
	
	game_history = Series.objects.filter(bowler=profile, league=league)
	
	series_data = []
	averages_data = []
	
	week_padding = 5
	num_weeks = ["Week " + str(n) for n in range(1, league.current_week+week_padding)]
	
	for game in game_history:
		series_average = int(game.scratch_score / 3)
		series_data.append(series_average)
		averages_data.append(game.applied_average)
		
		game.series_average = series_average
	
	return render(request, 'leagues/view_bowler.html', {'league' : league, 'bowler' : l_bowler, 'profile' : profile, 'game_history' : game_history, 'num_weeks' : num_weeks, 'series_data' : series_data, 'averages_data' : averages_data})
	

def view_weekly_tasks(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)

	
	return render(request, 'leagues/weekly/weekly_tasks.html', {'league' : league})


def export_rosters(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	rules = league.leaguerules
	week_number = league.week_pointer
	rules = league.leaguerules
	weekly_pairs_list = WeeklyPairings.objects.filter(league=league, week_number=week_number).order_by('lane_pair')
	
	team_numbers = []
	for pair in weekly_pairs_list:
		team_numbers.append(pair.team_one.id)
		team_numbers.append(pair.team_two.id)
	
	team_roster_dict={}
	for i in team_numbers:
		team =get_object_or_404(Team, league__bowling_center__name=center_name, league__name=league_name, number=i)
		rosters = TeamRoster.objects.filter(team=team, is_active=True).order_by('lineup_position')
		
		roster_dict = {}
		lineup_counter = 1
		for roster in rosters:
			
			bowler = get_object_or_404(BowlerProfile, id=roster.bowler.id)
			lb_record = get_object_or_404(LeagueBowler, league=league, bowler=bowler)
			
			applied_handicap = 0
			if rules.is_handicap:
				applied_handicap = int((rules.handicap_percentage / 100) * ( rules.handicap_scratch - lb_record.league_average))
				if applied_handicap < 0:
					applied_handicap = 0
			
			roster_dict.update({ bowler.id : {'first_name' : bowler.first_name, 'last_name' : bowler.last_name, 'league_average' : lb_record.league_average, 'applied_handicap' : applied_handicap}})
			lineup_counter += 1
		team_roster_dict.update({ team.number : roster_dict})
		
	if request.method == "POST":
		if league.current_week == 1: # Create a backup with blank scores for potential rescoring
			backup_week_number = 0
			league.create_weekly_score_backup(backup_week_number)
	
		export_filename = str(league.id) + '_' + str(week_number) +'.json'
		with open(ROSTERS_DIR + export_filename, 'w') as rf:
			dict_data = json.dumps(team_roster_dict, indent=4)
			rf.write(dict_data)
			
		return redirect('league-view-weekly-tasks', league.bowling_center.name, league.name)
		
	else:	
		return render(request, 'leagues/weekly/export_rosters.html', {'league': league, 'rosters' : team_roster_dict})


def finalize_week(request, center_name="", league_name=""):
	league= get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	if request.method == "POST":
		league.score_week(league.current_week)
		league.create_weekly_score_backup(league.current_week)
		
		league.advance_week()
		league.save()
	return redirect('league-view-weekly-tasks', center_name, league.name)
	

def import_scores(request, center_name="", league_name=""):
	league = get_object_or_404(League, name=league_name, bowling_center__name=center_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	week_number = league.week_pointer
	
	if request.method == 'POST':
		filename = str(league.id) + '_' + str(week_number) + '.json'
		
		with open(SCOREDIR + filename, 'r') as imports:
			imported = json.load(imports)
		
		date = imported["header"]["series_date"]
		
		for team in imported["teams"].items():
			t = get_object_or_404(Team, league=league, number=team[0])

			pair_number = team[1]["pair_number"]
			for bowler in team[1]["bowlers"].items():
				b = get_object_or_404(BowlerProfile, id=bowler[0])
				
				new_series = Series.objects.create(league=league, team=t, bowler=b, series_date=date, week_number=week_number, pair_number=pair_number)
				
				for k,v in bowler[1].items():
					setattr(new_series, k, v)
					new_series.save()
		
		messages.success(request, 'Scores imported successfully.')
		return redirect('edit-weekly-scores', league.bowling_center.name, league.name)
	else:
		import_form = ImportScoresForm()
		return render(request, 'leagues/weekly/import_scores.html', {'league' : league, 'import_form' : import_form })


def edit_scores(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	center = get_object_or_404(BowlingCenter, name=center_name)

	EditScoreFormSet = formset_factory(EditScoresForm, extra=0)
	
	weeks_scores = Series.objects.filter(league=league, week_number=league.week_pointer).order_by('pair_number')
	bowler_ids = []
	team_ids = []
	for score in weeks_scores:
		bowler_ids.append(score.bowler.id)
		team_ids.append(score.team.id)

	if request.method == 'POST':
		print(request.POST)
		edited_scores = EditScoreFormSet(request.POST)
		
		for form in edited_scores:
			if form.is_valid():
				series = get_object_or_404(Series, team=form.cleaned_data.get('team_id'), bowler=form.cleaned_data.get('bowler_id'))
				series.applied_average = form.cleaned_data.get('applied_average')
				
				handicap = (league.leaguerules.handicap_percentage / 100) * (league.leaguerules.handicap_scratch - series.applied_average)
				if handicap < 0:
					handicap = 0;
				series.applied_handicap = handicap
				
				series.game_one_score = form.cleaned_data.get('game_one_score')
				series.game_two_score = form.cleaned_data.get('game_two_score')
				series.game_three_score = form.cleaned_data.get('game_three_score')
				
				series.save()
				
		league.rescore(league.week_pointer)
		messages.success(request, 'Scores edited')
		return redirect('edit-weekly-scores', center.name, league.name)
		
	else:
		teams = Team.objects.filter(id__in=team_ids)
		scores = {}
		
		form_key = 0
		for team in teams:
			team_scores = weeks_scores.filter(team_id=team.id)
			for score in team_scores:
				bowler = get_object_or_404(BowlerProfile, id=score.bowler.id)
				scores.update({form_key : {'team_id' : team.id, 'team_name' : team.name, 'bowler_id' : bowler.id, 'bowler_name' : bowler.get_name, 'applied_average':  score.applied_average, 'applied_handicap' : score.applied_handicap, 'game_one_score' : score.game_one_score, 'game_two_score' : score.game_two_score, 'game_three_score' : score.game_three_score}})
				form_key+= 1
		
		score_formset = EditScoreFormSet(initial = scores)
	return render(request, 'leagues/weekly/edit_scores.html', {'league' : league, 'formset' : score_formset})
		

def manage_league(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	teams = Team.objects.filter(league=league)
	return render(request, 'leagues/manage/manage_league.html', {'league' : league, 'teams' : teams})
	
	
def manage_league_secretary(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name = center_name, name=league_name)
	if not request.user.is_superuser:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	if request.method == 'POST':
		
		form = UpdateLeagueSecretaryForm(request.POST)
		if form.is_valid():
			new_secretary = form.cleaned_data['secretary']
			
			old_secretary = league.secretary
			
			league.set_secretary(new_secretary)
			new_secretary.userprofile.set_league_secretary(True)
			new_secretary.userprofile.save()
			
			if old_secretary: #check to see if old secretary is still a league secretary in another league
				
				other_leagues = League.objects.filter(secretary__id=old_secretary.id)
				if not other_leagues:
					old_secretary.userprofile.set_league_secretary(False)
					old_secretary.userprofile.save()
			
		return redirect('manage-league', league.bowling_center.name, league.name)
	else:
		form = UpdateLeagueSecretaryForm()
		return render(request, 'leagues/manage/update_league_secretary.html', {'form': form })

	
def move_league(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
	
	if request.method == 'POST':
		form = MoveLeagueForm(request.POST)
		if form.is_valid():
			
			league.bowling_center = form.cleaned_data['bowling_center']
			league.save()	
		return redirect('manage-league', league.bowling_center.name, league.name)
	else:
		form = MoveLeagueForm()
	return render(request, 'leagues/manage/move_league_center.html', {'form' : form, 'league' : league })
	
	
def set_week(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
		
	if request.method == "POST":
		form = SetWeekForm(request.POST)
		if form.is_valid():
			league.week_pointer = form.cleaned_data['week_pointer']
			league.save()
			return redirect('league-view-weekly-tasks', league.bowling_center.name, league.name)
		else:
			return render(request, 'leagues/manage/set_week.html', {'form': form, 'league' : league})
	else:
		form = SetWeekForm(initial={'current_week' : league.current_week})
	return render(request, 'leagues/manage/set_week.html', {'form' : form, 'league' : league})
	
	
def update_weekly_pairings(request, center_name="", league_name="", week=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
		
	if week:
		week_number = week
	else:
		week_number = league.week_pointer
	
	PairingsFormSet = formset_factory(WeeklyPairingsForm, formset=WeeklyPairingsFormSet, extra=0)
	if week:
		pairs = WeeklyPairings.objects.filter(league=league, week_number=week_number).order_by('lane_pair')
	else: 
		pairs = WeeklyPairings.objects.filter(league=league, week_number=league.week_pointer).order_by('lane_pair')
	teams = {}
	for pair in pairs:
		
		key = pair.lane_pair - 1 #In order to use pair number as key, have to shift left to make first index 0
		teams.update({key : {'team_one' : pair.team_one.number, 'team_two' : pair.team_two.number}})
	
	if request.method == 'POST':
		formset = PairingsFormSet(request.POST)
		
		if formset.is_valid():
			lane_pair = 1;
			for form in formset:
				pairings = WeeklyPairings.objects.get(league=league, week_number=league.week_pointer, lane_pair=lane_pair)
				
				pairings.team_one = Team.objects.get(league=league, number=form.cleaned_data.get('team_one'))
				pairings.team_two = Team.objects.get(league=league, number=form.cleaned_data.get('team_two'))
				
				pairings.save()
				lane_pair += 1
				
			return redirect('update-weekly-pairings', league.bowling_center.name, league.name)
		
		else: #re-render page with validation errors in formset
			return render(request, 'leagues/weekly/update_pairings.html', {'week': week_number, 'league' : league, 'formset' : formset})
	else:		
		pairs_formset = PairingsFormSet(initial = teams)
		return render(request, 'leagues/weekly/update_pairings.html', {'week' : week_number, 'league' : league, 'formset' : pairs_formset})
	
	
def restart_league(request, center_name="", league_name=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	if auth_test(request, league) != True:
		return redirect('view-center-league-by-name', league.bowling_center.name, league.name)
		
	if request.method == 'POST':
		form = RestartLeagueForm(request.POST)
		if form.is_valid():
			league.reset_weekly_from_backup(0)
			league.current_week = 1;
			league.week_pointer = 1;
			league.save()
			WeeklyResults.objects.filter(league=league).delete()
			Series.objects.filter(league=league).delete()
			messages.success(request, 'League successfully restarted.')
			return redirect('manage-league', league.bowling_center.name, league.name)
	else:
		form = RestartLeagueForm()
	return render(request, 'leagues/manage/restart_league.html', {'league' : league, 'form' : form})
		