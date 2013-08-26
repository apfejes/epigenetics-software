''' This is a django config file, which controls traffic on the web server,
connecting functions in the view file with specific URLs '''

from django.conf.urls import patterns, url
# from django.views.generic import TemplateView
import views




urlpatterns = patterns('',
#   url(r'^home$',views.index,name='index'),
    url(r'^$', views.home_view, name = 'base'),
    url(r'^collections/', views.view_collections, name = 'collections'),
    url(r'^query_form/', views.view_query_form, name = 'query_form'),
#   url(r'^collections/name/', views.collections, name='collectionsname'),
#   url(r'^gene.svg/$', views.view_svg, name='gene'),
    url(r'^svgcode/$', views.send_svg, name = 'svgcode'),
#   url(r'^names/$', views.collections, name = 'collection_names'),
#   url(r'^methylation/', views.view_methylation, name = 'methylation'),
#   url(r'^svgmethylationcode/', views.methylation_code, name = 'methylation_code'),
#   url(r'^chipseq/', views.view_chipseq, name = 'chipseq'),
#   url(r'^svgchipseqcode/', views.chipseq_code, name = 'chipseq_code'),
    url(r'^query/', views.query, name = 'query'),
    url(r'^templatestyle/', views.query, name = 'query'),
    )
