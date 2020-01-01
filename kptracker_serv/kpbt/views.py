from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, RedirectView


# Create your views here.

def index(request):
	print(request.user.is_anonymous)
	print(request.user.is_authenticated)
	if request.user.is_authenticated:
		return redirect('view-profile-by-username', request.user.username)
	else:
		return render(request, 'index.html')


class IndexView(TemplateView):

	template_name = 'index.html'

class AboutView(TemplateView):
	
	template_name = 'about.html'
    
class FAQsView(TemplateView):
    template_name = 'faqs.html'