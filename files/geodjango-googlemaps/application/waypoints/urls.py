# Import django modules
from django.conf.urls.defaults import *


urlpatterns = patterns('application.waypoints.views',
    url(r'^$', 'index', name='waypoints-index'),
    url(r'^upload$', 'upload', name='waypoints-upload'),
    url(r'^search$', 'search', name='waypoints-search'),
    url(r'^save$', 'save', name='waypoints-save'),
)
