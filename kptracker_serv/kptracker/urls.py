"""kptracker_serv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from kpbt import views

urlpatterns = [
    path('admin/', admin.site.urls),
	#Use include() to add paths from the kpbt application
	path('kpbt/', include('kpbt.urls')),
	
	#Redirect base URL to our appen
	path('', RedirectView.as_view(url='/kpbt/', permanent=True)),	
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 #Use static() to add url mappings to serve static files during development
 
#Add Django site authentication URLs
urlpatterns += [
	path('users/', include('django.contrib.auth.urls')),
] 

