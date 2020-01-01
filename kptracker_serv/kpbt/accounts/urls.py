from django.urls import path
from kpbt.accounts import views

urlpatterns = [
	path('home', views.kpbt_user_home, name='user-home'),
	path('register', views.register, name="register"),
	path('create-profile', views.kpbt_user_create_profile, name='create-profile'),
	path('update-profile/<str:username>', views.kpbt_user_update_profile, name='update-profile-by-username'),
	path('profile/<str:username>', views.view_kpbt_user_bowler_profile, name='view-profile-by-username'),
	path('ajax/link_user', views.link_user, name='ajax-link-user'),
]