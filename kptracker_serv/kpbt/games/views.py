from django.shortcuts import redirect, render, get_object_or_404
#from kpbt.games.forms import CreateSeriesForm
from django.contrib.auth.decorators import permission_required
from kpbt.games.models import Series
from kpbt.leagues.models import League, LeagueBowler
from kpbt.teams.models import Team, TeamRoster
from kpbt.accounts.models import BowlerProfile
from kpbt.games.forms import ImportScoresForm, FilterScoresChartForm
from kptracker.settings import SCOREFILES_FOLDER as SCOREDIR
from django.http import JsonResponse, HttpResponse

import json
from datetime import datetime
		
def view_scores(request, center_name="", league_name="", week_number=""):
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	
	if week_number:
		#scores =[]
		
		#teams = league.teams.all()
		#for team in teams:
		scores = Series.objects.filter(league=league, week_number=int(week_number)).order_by('team')
		return render(request, 'games/view_scores_by_week.html', {'week_number' : week_number, 'scores' : scores})
	else:
		scores = Series.objects.filter(league=league).order_by('-week_number')
		return render(request, 'games/view_scores.html', {'week_number': week_number, 'scores' : scores})
