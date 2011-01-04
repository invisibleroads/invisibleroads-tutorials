# Import django modules
from django.conf.urls.defaults import *
from django.contrib import admin
# Import custom modules
import settings


admin.autodiscover()
urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'', include('googlemaps.waypoints.urls')),
)
