from django.contrib import admin
from kpbt.accounts.models import UserProfile
from django.contrib.auth.models import User, Permission


# Register your models here.
'''
def promote_to_center_manager(modeladmin, request, queryset):
	queryset.update(is_center_manager=True)
	#queryset.update(first_name='Big Time Manager')
	#user = queryset.filter('user__id = id')
	#user.user_permissions.add('kpbt.add_bowlingcenter')
	#queryset.update(user__user_permissions.add('kpbt.add_bowlingcenter'))
	promote_to_center_manager.short_description = "Promote user to Bowling Center Manager."
	
#	
class CenterAdmin(admin.ModelAdmin):
	#list_display = ['user.username', 'is_center_manager']
	#ordering = ['user.username']
	actions = [promote_to_center_manager]
	
admin.site.register(UserProfile, CenterAdmin)

'''