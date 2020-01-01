from django.urls import path, include
from kpbt import views
from kpbt.centers import views as center_views
from kpbt.leagues import views as league_views
from kpbt.teams import views as team_views


league_patterns = [
	
	
	#Paths that map to league-team functions
	path('teams/', include('kpbt.teams.urls')),
	
	#Paths that map to league-game functions
	path('games/', include('kpbt.games.urls')),
	
	path('leagues/', include('kpbt.leagues.urls')),
	
	
	path('<str:league_name>', league_views.view_league, name='view-center-league-by-name'),
	path('<str:league_name>/', include('kpbt.leagues.urls')),

]

urlpatterns=[
	
	#Path that maps to site root
	path('', views.index, name="index"),
	path('about', views.AboutView.as_view(), name="about"),
    path('faqs', views.FAQsView.as_view(), name="faqs"),
	
	#Paths that map to bowling center functions
	path('centers/', include('kpbt.centers.urls')),
	
	#Paths that map to user account functions
	path('accounts/', include('kpbt.accounts.urls')),
	
	
	
	#Paths that map to league functions
	path('leagues/', include('kpbt.leagues.urls')),
	
	#Paths that map to team functions
	path('teams/', include('kpbt.teams.urls')),
	
	#Paths that map to game functions
	path('games/', include('kpbt.games.urls')),

	
	#kpbt/<center_name>/ paths
	path('<str:center_name>', center_views.view_center_home, name='view-center-by-name'),
	path('<str:center_name>/', include('kpbt.centers.urls')),
	path('<str:center_name>/', include(league_patterns)),



]

