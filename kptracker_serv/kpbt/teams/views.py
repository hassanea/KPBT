from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.forms import modelformset_factory, formset_factory
from kpbt.teams.forms import CreateTeamForm, TeamRosterForm, ExistingBowlerForm, UpdateTeamForm, NewRosterForm, UpdateRosterForm #RosterFormSet
from kpbt.teams.models import Team, TeamRoster
from kpbt.leagues.models import League, LeagueBowler, WeeklyResults
from kpbt.centers.models import BowlingCenter
from kpbt.accounts.models import BowlerProfile
from num2words import num2words


def view_team(request, center_name= "", league_name="", team_name=""):
	if center_name:
		center = get_object_or_404(BowlingCenter, name=center_name)
		if league_name:
			league= get_object_or_404(League, name=league_name)
			if team_name:
				team = get_object_or_404(Team, league__bowling_center__name=center_name, league__name=league_name, name=team_name)
				bowlers = team.roster.filter(roster_record__is_active=True)
				
				
				for bowler in bowlers:
					lb = LeagueBowler.objects.get(bowler=bowler)
					bowler.__dict__.update({'games_bowled' : lb.games_bowled, 'league_average' : lb.league_average, 'league_high_scratch_game' : lb.league_high_scratch_game, 'league_high_handicap_game' : lb.league_high_handicap_game, 'league_high_handicap_series' : lb.league_high_handicap_series, 'league_high_scratch_series' : lb.league_high_scratch_series, 'league_total_scratch' : lb.league_total_scratch, 'league_total_handicap' : lb.league_total_handicap})
					
					
				results = WeeklyResults.objects.filter(team=team, league=league).order_by('week_number')
				num_weeks = ["Week " + str(n) for n in range(1, league.schedule.num_weeks+1)]
				
				points_won = []
				points_lost = []
				for result in results:
					points_won.append(result.points_won)
					points_lost.append(result.points_lost)
				
				
			
				return render(request, 'teams/view_team.html', {'team' : team, 'bowlers' : bowlers, 'num_weeks' : num_weeks, 'points_won' : points_won, 'points_lost': points_lost })
			else:
				teams = Team.objects.filter(league__bowling_center__name=center_name, league__name=league_name)
				return render(request, 'teams/team_home.html', {'teams' : teams })
	else:
		teams = Team.objects.all().order_by('-league__bowling_center__name', 'league__name', 'number')
		print(teams)
		return render(request, 'teams/team_home.html', {'teams' : teams})
	
	
def update_team(request, center_name="", league_name="", team_name=""):
	team = get_object_or_404(Team, league__bowling_center__name=center_name, league__name=league_name, name=team_name)
	
	if request.method == "POST":
		form = UpdateTeamForm(request.POST, instance=team)
		if form.is_valid():
			updated = form.save()
			
			return redirect('manage-team', updated.league.bowling_center.name, updated.league.name, updated.name)
	else:
		form = UpdateTeamForm(instance=team)
	return render(request, 'teams/manage/update_team.html', {'form': form, 'team' : team})

		
def manage_team(request, center_name= "", league_name="", team_name=""):
	league = get_object_or_404(League, bowling_center__name= center_name, name=league_name)
	team = get_object_or_404(Team, league=league, name=team_name)
	team_rosters = TeamRoster.objects.filter(team_id=team.id, is_active=True)
	bowler_data = []
	for roster in team_rosters:
		id = roster.bowler.id
		bowler_data.append(id)
		
	bowlers = BowlerProfile.objects.filter(id__in=bowler_data, is_linked=False).values()
	
	for bowler in bowlers:
		lb = get_object_or_404(LeagueBowler, league=league, bowler=bowler['id'])
		bowler.update({'average' : lb.league_average})
	
	ExistingRosterFormSet= formset_factory(UpdateRosterForm, extra=0)
	NewRosterFormSet = formset_factory(NewRosterForm, extra=4)
	
	if request.method == 'POST':
		if request.POST.get("update_name", ""):
			name_form = UpdateTeamForm(request.POST, instance=team)
			if name_form.is_valid():
				name_form.save()
				team = get_object_or_404(Team, name=name_form.cleaned_data.get('name'))
				
		elif request.POST.get("add_existing", ""):
			lb = get_object_or_404(LeagueBowler, id=request.POST.get("bowler"))
			bp = lb.bowler
			team_roster_record, created = TeamRoster.objects.get_or_create(bowler=bp, team=team)
			team_roster_record.is_active=True
			team_roster_record.save()
			
		elif request.POST.get("remov_existing", ""):
			lb = get_object_or_404(LeagueBowler, id=request.POST.get("bowler"))
			bp = lb.bowler
			tr_record = TeamRoster.objects.get(team=team, bowler=bp)
			tr_record.is_active=False
			tr_record.save()
			
		
		else:
			if request.POST.get("new", ""):
				formset = NewRosterFormSet(request.POST)
			elif request.POST.get("update", ""):
				formset = ExistingRosterFormSet(request.POST)
			
			for form in formset:
				if form.is_valid():
					id = form.cleaned_data.get('id')
					first_name = form.cleaned_data.get('first_name')
					last_name = form.cleaned_data.get('last_name')
					hand = form.cleaned_data.get('hand')
					designation = form.cleaned_data.get('designation')
					gender = form.cleaned_data.get('gender')
					average = form.cleaned_data.get('average')
					
					if not id:
						bp = BowlerProfile.objects.create(first_name=first_name, last_name=last_name, hand=hand, designation=designation, gender=gender)
						LeagueBowler.objects.create(league=league, bowler= bp, league_average=average)
						TeamRoster.objects.create(team=team, bowler=bp)
						
					else:	
						updated = get_object_or_404(BowlerProfile, id=id)
						updated.first_name = first_name
						updated.last_name = last_name
						updated.hand = hand
						updated.designation = designation
						updated.gender = gender
						updated.save()
						
						lb = get_object_or_404(LeagueBowler, league=league, bowler=id)
						lb.league_average = average
						lb.save()
		print(team)			
		return redirect('manage-team', center_name, league_name, team.name)
	
	else:
	
		team_name_form = UpdateTeamForm(instance=team)
	
	
		rosterset = ExistingRosterFormSet(initial = bowlers)
		new_formset = NewRosterFormSet()
		
		#get league bowlers not already on a team roster in this league
		league_team_rosters = TeamRoster.objects.filter(team__league__name = league_name, is_active=False)
		
		bowler_ids = []
		for roster in league_team_rosters:
			bowler_ids.append(roster.bowler.id)
		inactive_bowlers = LeagueBowler.objects.filter(bowler__id__in=bowler_ids)
		
		eadd_form = ExistingBowlerForm()
		eadd_form.fields['bowler'].queryset = inactive_bowlers
		
		current = LeagueBowler.objects.filter(league=league, bowler__in=bowler_data)
		eremov_form = ExistingBowlerForm()
		eremov_form.fields['bowler'].queryset = current
		
		return render(request, 'teams/manage/manage_team.html', {'league': league, 'team': team, 'name_form' : team_name_form, 'rosterset' : rosterset, 'new_formset' : new_formset, 'eadd_form' : eadd_form, 'eremov_form' : eremov_form})		
	