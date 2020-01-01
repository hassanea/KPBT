from django.urls import path, include
from kpbt.centers import views

center_management_patterns = [
	path('', views.center_management_home, name='center-management-home'),
	path('update-manager', views.update_manager, name='update-center-manager'),
	path('update-center', views.update_center, name='update-center'),
	path('manage-leagues', views.manage_leagues, name='manage-center-leagues'),
	path('delete-league/<str:league_name>', views.delete_league, name='delete-center-league'),
]

urlpatterns =[
	path('create', views.create_bowling_center, name='create-bowling-center'),
	path('locations', views.center_locations, name='center_locations'),
	path('', views.view_center_home, name='center-home'),
	path('create', views.create_bowling_center, name='create-bowling-center'),
	path('center-management/', include(center_management_patterns)),

	path('manage/', include(center_management_patterns)),
]
	