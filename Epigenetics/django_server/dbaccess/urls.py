''' This is a django config file, which controls traffic on the web server,
connecting functions in the view file with specific URLs '''

from django.conf.urls import patterns, url, include
# from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()
import views

urlpatterns = patterns('',
#   url(r'^home$',views.index,name='index'),
    url(r'^$', views.home_view, name = 'base'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^loginpage/', views.loginpage, name = 'loginpage'),
    url(r'^compound/', views.compound, name = 'compound'),
    url(r'^createuser/', views.createuser, name = 'createuser'),
    url(r'^authenticate/', views.login_view, name = 'authenticate'),
    url(r'^logout/', views.logout_view, name = 'logout'),
    url(r'^query_form/', views.view_query_form, name = 'query_form'),
    url(r'^metadata/', views.view_metadata, name = 'metadata'),
    url(r'^metadata2/', views.view_metadata2, name = 'metadata2'),
    url(r'^metadata3/', views.view_metadata3, name = 'metadata3'),
    url(r'^collections/', views.view_collections, name = 'collections'),
    url(r'^deletesample/', views.delete_sample, name = 'delete_sample'),
#   url(r'^collections/name/', views.collections, name='collectionsname'),
#   url(r'^gene.svg/$', views.view_svg, name='gene'),
  #  url(r'^svgcode/$', views.send_svg, name = 'svgcode'),
#   url(r'^names/$', views.collections, name = 'collection_names'),
#   url(r'^methylation/', views.view_methylation, name = 'methylation'),
#   url(r'^svgmethylationcode/', views.methylation_code, name = 'methylation_code'),
#   url(r'^chipseq/', views.view_chipseq, name = 'chipseq'),
#   url(r'^svgchipseqcode/', views.chipseq_code, name = 'chipseq_code'),
#   url(r'^query/', views.query, name = 'query'),
#   url(r'^templatestyle/', views.query, name = 'query'),
    )
