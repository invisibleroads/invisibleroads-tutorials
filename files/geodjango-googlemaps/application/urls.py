# Import django modules
from django.conf.urls.defaults import *
from django.contrib import admin
# Import custom modules
import settings


admin.autodiscover()


urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'', include('application.waypoints.urls')),
)


if settings.DEBUG:
    # Set
    mediaURL = settings.MEDIA_URL[1:] if settings.MEDIA_URL.startswith('/') else settings.MEDIA_URL
    # Extend
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % mediaURL, 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
