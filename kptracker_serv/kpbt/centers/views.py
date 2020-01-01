from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from kpbt.centers.forms import CreateBowlingCenterForm, UpdateManagerForm, CreateCenterAddressForm, UpdateCenterForm, UpdateAddressForm, DeleteLeagueForm
from kpbt.leagues.forms import LeagueCreationForm
from kpbt.centers.models import BowlingCenter, CenterAddress
from kpbt.accounts.models import UserProfile
from kpbt.leagues.models import League
from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

@permission_required('kpbt.add_bowlingcenter')
def create_bowling_center(request):
	if request.method == 'POST':
		center_form = CreateBowlingCenterForm(request.POST)
		address_form = CreateCenterAddressForm(request.POST)
		
		if center_form.is_valid() and address_form.is_valid():
			manager = center_form.cleaned_data['manager']
			manager.userprofile.set_center_manager(True)
			manager.userprofile.save()
			new_center = center_form.save()
			
			address = address_form.save(commit=False)
			address.bowling_center = new_center
			address.save()
			
			messages.success(request,'Center created.')
			return redirect('view-center-by-name', new_center.name)
	else:
		center_form = CreateBowlingCenterForm()
		address_form = CreateCenterAddressForm()
		
	return render(request, 'centers/manage/create_center.html', {'center_form': center_form, 'address_form' : address_form})


def view_center_home(request, center_name=""):
	if center_name:	
		center = get_object_or_404(BowlingCenter, name=center_name)
		address = get_object_or_404(CenterAddress, bowling_center=center)
		manager = center.manager.username
		
		
		leagues = center.leagues.all()
		return render(request, 'centers/view_center.html', {'center' : center, 'leagues' : leagues, 'address' : address, 'manager' : manager})
	else:
		centers = BowlingCenter.objects.all().annotate(num_leagues=Count('leagues'))
		league_c = BowlingCenter.objects.annotate(num_leagues=Count('leagues'))
		return render(request, 'centers/center_home.html', {'centers' : centers, 'leagues' : league_c})
		
		
def center_management_home(request, center_name=""):
	if center_name:
		center = get_object_or_404(BowlingCenter, name=center_name)
		return render(request, 'centers/manage/manage_center.html', {'center' : center})
	else:
		center = get_object_or_404(BowlingCenter, name=request.user.center_managed.name)
		return render(request, 'centers/manage/manage_center.html', {'center' : center })
	
	
def update_center(request, center_name=""):
	center = get_object_or_404(BowlingCenter, name=center_name)
	address = get_object_or_404(CenterAddress, bowling_center = center)
	
	if request.method == 'POST':
		update_center_form = UpdateCenterForm(request.POST, instance=center)
		update_address_form = UpdateAddressForm(request.POST, instance=address)
		
		if update_center_form.is_valid() and update_address_form.is_valid():
			update_center_form.save()
			update_address_form.save()
			messages.success(request, 'Center updated.')
			return redirect('center-management-home', center.name)
		else:
			messages.warning(request, 'Please fix form error.')
			
	else:
		update_center_form = UpdateCenterForm(instance=center)
		update_address_form = UpdateAddressForm(instance=address)
	return render(request, 'centers/manage/update_center.html', {'center' : center, 'update_center_form' : update_center_form, 'update_address_form' : update_address_form})
		

def update_manager(request, center_name =""):
	center = get_object_or_404(BowlingCenter, name=center_name)
	if request.method == 'POST':
		update_manager_form = UpdateManagerForm(request.POST)
		if update_manager_form.is_valid():
			center.manager.userprofile.set_center_manager(False)
			center.manager.userprofile.save()
			new_manager = update_manager_form.cleaned_data['manager']
			center.set_manager(new_manager)
			new_manager.userprofile.set_center_manager(True)
			new_manager.userprofile.save()
			
			center.save()
			messages.success(request, 'Manager updated.')
			return redirect('center-management-home', center.name)
				
	else:
		update_manager_form = UpdateManagerForm()
	return render(request, 'centers/manage/update_manager.html', {'center' : center, 'form' : update_manager_form})


def center_locations(request):
    return render(request, 'centers/center_locations.html')

	
def manage_leagues(request, center_name=""):
	center = get_object_or_404(BowlingCenter, name=center_name)
	leagues = League.objects.filter(bowling_center__name=center_name)
	return render(request, 'centers/manage/manage_leagues.html', {'leagues' : leagues, 'center' : center })
	
	
def delete_league(request, center_name="", league_name=""):
	center= get_object_or_404(BowlingCenter, name=center_name)
	league = get_object_or_404(League, bowling_center__name=center_name, name=league_name)
	
	if request.method == 'POST':
		form = DeleteLeagueForm(request.POST)
		
		if form.is_valid():
			league.delete()
			messages.success(request, 'League deleted')
			return redirect('center-management-home', center.name)
	else:
		form = DeleteLeagueForm()
	return render(request, 'centers/manage/delete_league.html', {'league' : league, 'center' : center, 'form' : form})