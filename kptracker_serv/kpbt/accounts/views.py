from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from kpbt.accounts.forms import RegisterForm, CreateUserBowlerProfileForm, UpdateUserBowlerProfileForm #, CreateUserProfileForm
from kpbt.accounts.models import UserProfile, BowlerProfile, Links
from kpbt.leagues.models import LeagueBowler
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse


def register(request):
	if request.method == 'POST':
		new_user_form = RegisterForm(request.POST)
		if new_user_form.is_valid():
			new_user = new_user_form.save()
			user_email = new_user_form.cleaned_data['email']
			user_profile = UserProfile.objects.create(user= new_user, email= user_email)

			user_profile.save()
					
			username = new_user_form.cleaned_data.get('username')
			raw_password = new_user_form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('create-profile')
	else:
		new_user_form = RegisterForm()
	return render(request, 'registration/register.html', {'form': new_user_form})


def kpbt_user_home(request):
	print(request)
	return redirect('view-profile-by-username', request.user.username)

@login_required
def kpbt_user_create_profile(request, username=""):
	if request.method == 'POST':
		bowler_profile_form = CreateUserBowlerProfileForm(request.POST)
		
		if bowler_profile_form.is_valid():
			new_profile = bowler_profile_form.save(commit=False)
			new_profile.user = request.user
			new_profile.save()
			return redirect('view-profile-by-username', request.user.username)
	else:
		user = get_object_or_404(User, username=request.user.username)
		bowler_profile_form = CreateUserBowlerProfileForm()
	return render(request, 'accounts/create_profile.html', {'profile_form' : bowler_profile_form})
	
	
@login_required
def kpbt_user_update_profile(request, username=""):
	if request.method == 'POST':
		bowler_profile_form = UpdateUserBowlerProfileForm(request.POST, instance=request.user.bowlerprofile)
		
		if bowler_profile_form.is_valid():
			bowler_profile_form.save()
			return redirect('view-profile-by-username', request.user.username)
	else:
		user = get_object_or_404(User, username=request.user.username)
		bowler_profile_form = UpdateUserBowlerProfileForm(instance = user.bowlerprofile)
	return render(request, 'accounts/update_profile.html', {'profile_form' : bowler_profile_form })
	

@login_required			
def view_kpbt_user_bowler_profile(request, username= ""):
	if username:
		try:
			bp = BowlerProfile.objects.get(user__username=username)
		except ObjectDoesNotExist:
			return redirect('create-profile')
		else:
			bp = get_object_or_404(BowlerProfile, user__username=username)
			
			lb_ids = []
			linked_bowlers = Links.objects.filter(type='B', user=request.user)
			for link in linked_bowlers:
				lb_ids.append(link.type_id)
			lb_profiles = LeagueBowler.objects.filter(id__in =lb_ids)
			print(lb_profiles)
		return render(request, 'accounts/view_profile.html', {'bp' : bp, 'lb_profiles' : lb_profiles})
		
		
def link_user(request):
	if request.method == 'POST' and request.is_ajax():
		print('Is ajax!')
		print(request.POST)
		type = request.POST.get('type')
		lb_id = request.POST.get('lb_id')
		bowler = get_object_or_404(LeagueBowler, id=lb_id)
		
		if type == 'bowler':
			new_link = Links.objects.create(type='B', type_id = lb_id, user_id = request.user.id)
			new_link.save()
		data = {}
			
		return JsonResponse(data)
	