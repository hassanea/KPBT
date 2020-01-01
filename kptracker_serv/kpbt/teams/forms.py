from django import forms
from kpbt.teams.models import Team, TeamRoster
from kpbt.accounts.models import BowlerProfile
from kpbt.leagues.models import LeagueBowler
from django.contrib.auth.models import User
from django.forms import formset_factory
from kpbt.accounts.forms import CreateUserBowlerProfileForm, UpdateUserBowlerProfileForm

class CreateTeamForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('league', 'number', 'name')
		
		
class TeamRosterForm(forms.ModelForm):
	class Meta:
		model = BowlerProfile
		fields = ('__all__')
	
	
class UpdateRosterForm(forms.Form):
	id = forms.IntegerField(widget=forms.HiddenInput)
	first_name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'aria-label':'First Name'}))
	last_name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'aria-label':'Last Name'}))
	hand = forms.ChoiceField(choices= (('R', 'Right'), ('L', 'Left')))
	designation = forms.ChoiceField(choices=(('A', 'Adult'), ('J', 'Junior'), ('S', 'Senior')))
	gender = forms.ChoiceField(choices= (('M', 'Male'), ('F', 'Female')))
	average = forms.IntegerField(min_value=0, max_value=300)
	
	def clean(self):
		cleaned_data = super().clean()
		
class NewRosterForm(forms.Form):
	first_name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'aria-label':'First Name'}))
	last_name = forms.CharField(max_length=32, widget=forms.TextInput(attrs={'aria-label':'Last Name'}))
	hand = forms.ChoiceField(choices= (('R', 'Right'), ('L', 'Left')))
	designation = forms.ChoiceField(choices=(('A', 'Adult'), ('J', 'Junior'), ('S', 'Senior')))
	gender = forms.ChoiceField(choices= (('M', 'Male'), ('W', 'Female')))
	average = forms.IntegerField(min_value=0, max_value=300)
	
	def clean(self):
		cleaned_data = super().clean()
		
	
class ViewRosterForm(forms.ModelForm):

	league_average = forms.IntegerField()

	class Meta:
		model = BowlerProfile
		fields = ('first_name', 'last_name', 'league_average')

class DeleteRosterForm(forms.ModelForm):
	
	delete_roster = forms.BooleanField()
	
	class Meta:
		model = TeamRoster
		fields = ('bowler',)

class ExistingBowlerForm(forms.ModelForm):
	
	class Meta:
		model = LeagueBowler
		fields = ('bowler',)
		
class UpdateTeamForm(forms.ModelForm):
	class Meta:
		model = Team
		fields = ('name',)