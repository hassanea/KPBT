from django.urls import path, include
from kpbt.teams import views

urlpatterns = [
	path('', views.view_team),
	path('home', views.view_team, name='team-home'),
	path('view-team/<str:team_name>', views.view_team, name='view-team'),
	path('manage/', views.manage_team, name='manage-team'),
]