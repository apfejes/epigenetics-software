'''Root url file for the django web server'''

from django.conf.urls import patterns, include, url


# Uncomment the next two lines to enable the admin:

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),
    # url(r'^collections/', views.view_collections, name = 'collections'),
    url(r'^dbaccess/', include('dbaccess.urls')),
)
