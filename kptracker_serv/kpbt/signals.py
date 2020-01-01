from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .accounts.models import UserProfile

@receiver(post_save, sender=UserProfile)
def perms_update(sender, instance, **kwargs):
	if instance.is_center_manager:
		user = instance.user
		user.user_permissions.add('kpbt.add_bowlingcenter')
		print('we got here')
		user.save()
		
"""
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
		BowlerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
	instance.userprofile.save()
	instance.bowlerprofile.save()
"""