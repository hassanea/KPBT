from django import forms
from django.forms.formsets import BaseFormSet
from kpbt.leagues.models import League, LeagueRules, Schedule, WeeklyPairings
from kpbt.centers.models import BowlingCenter



class LeagueCreationForm(forms.ModelForm):
	
	league_name = forms.CharField(max_length=32, widget= forms.TextInput(attrs={'placeholder':'League name', 'class':'text-center', 'aria-label':'League Name'}))
	num_teams = forms.IntegerField(widget = forms.NumberInput(attrs={'placeholder':'Number of teams', 'class':'text-center', 'aria-label':'Number of Teams'}))
	playing_strength = forms.IntegerField(widget = forms.NumberInput(attrs={'placeholder':'Playing strength', 'class':'text-center', 'aria-label':'Playing Strength'}))
	max_roster_size = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Maximum roster size', 'class':'text-center', 'aria-label':'Max Roster Size'}))
	entering_average = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Entering average'}))
	handicap_scratch = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Scratch figure', 'class':'text-center', 'aria-label':'Scratch Figure'}))
	handicap_percentage = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Handicap percentage', 'class':'text-center', 'aria-label':'Handicap Percentage'}))
	bye_team_point_threshold = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Bye-Team point diff', 'class':'text-center', 'aria-label':'Bye-Team Point Difference'}))
	absentee_score = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Blind score', 'class':'text-center', 'aria-label':'Blind Score'}))
	game_point_value = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Game point value', 'class':'text-center', 'aria-label':'Game Point Value'}))
	series_point_value = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Series point value', 'class':'text-center', 'aria-label':'Series Point Value'}))
	
	class Meta:
		model = LeagueRules
		fields = ('league_name', 'num_teams', 'designation', 'gender', 
			'playing_strength', 'max_roster_size', 'is_handicap', 'handicap_scratch', 'handicap_percentage',
			'bye_team_point_threshold', 'absentee_score', 'game_point_value', 'series_point_value')
	
	
class UpdateLeagueRulesForm(forms.ModelForm):
	class Meta:
		model = LeagueRules
		fields = ('designation', 'gender', 'max_roster_size', 'handicap_scratch', 'handicap_percentage', 
			'bye_team_point_threshold', 'absentee_score', 'game_point_value', 'series_point_value')
			
class RenameLeagueForm(forms.ModelForm):
	class Meta:
		model = League
		fields = ('name',)
		
class CreateScheduleForm(forms.ModelForm):
	
	date_starting = forms.DateField(widget= forms.DateInput(attrs={'placeholder':'Start date', 'class':'text-center', 'aria-label':'Start Date'}))
	date_ending = forms.DateField(widget=forms.DateInput(attrs={'placeholder':'End date', 'class':'text-center', 'aria-label':'End Date'}))
	start_time = forms.TimeField(widget=forms.TimeInput(attrs={'placeholder':'Starting time', 'class':'text-center', 'aria-label':'Start Time'}))
	
	class Meta:
		model = Schedule
		fields = ('date_starting', 'date_ending', 'day_of_week', 'start_time')
		
class UpdateScheduleForm(forms.ModelForm):
	class Meta:
		model = Schedule
		fields = ('date_starting', 'date_ending', 'day_of_week', 'start_time')
		
class UpdateLeagueSecretaryForm(forms.ModelForm):
	class Meta:
		model = League
		fields = ('secretary',)
		
class MoveLeagueForm(forms.ModelForm):
	class Meta:
		model = League
		fields=('bowling_center',)
		
class SetWeekForm(forms.Form):
	week_pointer = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder':'Set Week Number'}))
	current_week = forms.IntegerField(widget=forms.HiddenInput())
	
	def clean(self):
		cleaned_data = super().clean()
		
		week_pointer = cleaned_data.get('week_pointer')
		current_week = cleaned_data.get('current_week')
		
		if (week_pointer <=0):
			raise forms.ValidationError(
				"Week must be greater than 0."
			)
		elif (week_pointer > current_week):
			raise forms.ValidationError(
				"Week must be less than current week number"
				)

class WeeklyPairingsForm(forms.Form):
	team_one = forms.IntegerField(widget=forms.NumberInput(attrs={'aria-label':'Enter a team # from 1 to 10'}))
	team_two= forms.IntegerField(widget=forms.NumberInput(attrs={'aria-label':'Enter a team # from 1 to 10'}))
	
	def clean(self):
		cleaned_data = super().clean()
	
				
class WeeklyPairingsFormSet(BaseFormSet):
		def clean(self):
			if any(self.errors):
				print('formset_error')
				return
			teams = []
			for form in self.forms:
				t_one = form.cleaned_data.get('team_one')
				if t_one in teams:
					raise forms.ValidationError("Team cannot bowl on two lanes.")
				teams.append(t_one)
				print(t_one)
				t_two = form.cleaned_data.get('team_two')
				if t_two in teams:
					raise forms.ValidationError("Team cannot bowl on two lanes.")
				print(t_two)
				teams.append(t_two)
				
				
class RestartLeagueForm(forms.Form):
	restart_confirmation = forms.CharField(max_length=7)
	
	def clean(self):
		cleaned_data=super().clean()
		
		confirmation = cleaned_data.get("restart_confirmation")
		
		if confirmation:
			if confirmation != "RESTART":
				raise forms.ValidationError(
					"Please enter RESTART to confirm league restart."
				)
	
			