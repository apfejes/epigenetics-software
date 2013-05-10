from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

import views

urlpatterns = patterns('',
	url(r'^$',views.index,name='index'),
	url(r'^collections/$', 
		TemplateView, 
		{'template': 'collections.jade'}, 
		name='collections'	
		)
)
