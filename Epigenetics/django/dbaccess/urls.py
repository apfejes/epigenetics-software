from django.conf.urls import patterns, url
#from django.views.generic import TemplateView
import views



urlpatterns = patterns('',
#	url(r'^home$',views.index,name='index'),
	url(r'^$', views.my_view, name='base'),
	url(r'^collections/', views.view_collections, name='collections'),
	url(r'^collections/name/', views.collections, name='collectionsname'),
#	url(r'^gene.svg/$', views.view_svg, name='gene'),
	url(r'^svgcode/$', views.send_svg, name='svgcode'),
	)
	
