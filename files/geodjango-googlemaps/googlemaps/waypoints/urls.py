# Import django modules
from django.conf.urls.defaults import *


urlpatterns = patterns('googlemaps.waypoints.views',
    url(r'^$', 'index', name='waypoints-index'),
    url(r'^save$', 'save', name='waypoints-save'),
    url(r'^search$', 'search', name='waypoints-search'),
    url(r'^upload$', 'upload', name='waypoints-upload'),
)
