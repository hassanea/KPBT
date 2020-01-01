from django import forms
from kpbt.accounts.models import UserProfile, BowlerProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
	email = forms.EmailField()
	
	class Meta:
		model = User 
		fields = ('username', 'email', 'password1', 'password2', )
	
class CreateUserBowlerProfileForm(forms.ModelForm):
	
	class Meta:
		model = BowlerProfile
		fields = ('first_name', 'last_name', 'hand', 'designation', 'gender')
		
		
class UpdateUserBowlerProfileForm(forms.ModelForm):
		
	class Meta:
		model = BowlerProfile
		exclude = ['user', 'is_linked']
		fields = ('first_name', 'last_name', 'hand', 'designation', 'gender',)
		
