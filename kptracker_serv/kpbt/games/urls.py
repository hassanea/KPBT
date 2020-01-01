from django.urls import path
from kpbt.games import views


urlpatterns = [
	path('', views.view_scores, name='scores-home'),
	path('<str:week_number>', views.view_scores, name='view-scores-by-week'),
]

