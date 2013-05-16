from django.conf.urls import patterns, include, url
#from django.views.generic import TemplateView
import views



urlpatterns = patterns('',
#	url(r'^home$',views.index,name='index'),
	url(r'^$', views.my_view, name='base'),
	url(r'^collections/', views.view_collections, name='collections')
	)
	
