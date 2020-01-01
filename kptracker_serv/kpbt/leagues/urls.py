from django.urls import path, include
from kpbt.leagues import views
from kpbt.teams import views as team_views
from kpbt.games import views as series_views

league_management_paterns = [
	path('', views.manage_league, name='manage-league'),
	path('update-league-secretary', views.manage_league_secretary, name='update-league-secretary'),
	path('move-league', views.move_league, name='move-league'),
	path('update-league', views.update_league, name='update-league'),
	path('set-week', views.set_week, name='set-week'),
	path('restart-league', views.restart_league, name='restart-league'),	
]

weekly_patterns = [
	path('', views.view_weekly_tasks, name='league-view-weekly-tasks'),
	path('export-rosters', views.export_rosters, name='view-export-rosters'),
	path('update-pairings', views.update_weekly_pairings, name='update-weekly-pairings'),
	path('update-pairings/<int:week>', views.update_weekly_pairings, name='update-pairing-by-week'),
	path('import-scores', views.import_scores, name='import-scores'),
	path('view-scores/<str:week_number>', series_views.view_scores, name='league-view-scores-by-week'),
	path('edit-scores', views.edit_scores, name='edit-weekly-scores'),
	path('finalize-week', views.finalize_week, name='finalize-week'),
]

team_patterns = [
	path('teams', team_views.view_team, name='teams-home'),
	path('teams/', include('kpbt.teams.urls')),
	path('<str:team_name>', team_views.view_team, name='view-center-league-team-by-name'),
	path('<str:team_name>/', include('kpbt.teams.urls')),
]

series_patterns = [
	path('', include('kpbt.games.urls')),
]


urlpatterns = [
	path('', views.view_league, name='league-home'),
	path('create-league', views.create_league, name='create-league'),
	path('view-league/', views.view_league, name='view-league-home'),
	path('<int:bowler_id>', views.view_league_bowler, name='view-league-bowler'),
	path('view-schedule', views.view_schedule, name='view-center-league-schedule'),
	path('weekly/', include(weekly_patterns)),
	path('manage/', include(league_management_paterns)),
	path('', include(team_patterns)),
	path('scores/', include(series_patterns)),
]