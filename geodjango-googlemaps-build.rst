Build a simple GIS web application using GeoDjango and Google Maps
==================================================================
By the end of this tutorial you will have built a simple GIS web application for viewing, editing, searching and uploading GIS data.  We first presented this tutorial as part of a three-hour session on `Working with Geographic Information Systems in Python <http://us.pycon.org/2009/tutorials/schedule/1PM4/>`_ during the `2009 Python Conference <http://us.pycon.org/2009/>`_ in Chicago, Illinois.

.. raw:: html

    <object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/Dfd5lzrz7ps&hl=en&fs=1&rel=0"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/Dfd5lzrz7ps&hl=en&fs=1&rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>


Example
--------
Make sure that GeoDjango is installed; see :doc:`geodjango-install`

**If you are running a 64-bit system, you may have to patch GeoDjango**; see :ref:`geodjango-patch`

Start PostgreSQL server
::
    
    su
    service postgresql start
    exit

Create PostgreSQL user and PostGIS database
::

    su - postgres
    createuser YOUR-USERNAME
    createdb -T template_postgis -O YOUR-USERNAME geodjango-googlemaps
    exit

Download the :download:`code and data <files/geodjango-googlemaps.zip>`
::
    
    wget http://invisibleroads.com/tutorials/_downloads/geodjango-googlemaps.zip
    unzip geodjango-googlemaps.zip
    cd geodjango-googlemaps

Create database configuration file ".database" with the following information on each line
::

    geodjango-googlemaps
    YOUR-USERNAME
    YOUR-PASSWORD

Setup tables
::
    
    python manage.py syncdb

Run server
::
    
    python manage.py runserver

Go to http://localhost:8000 and experiment with the application

1. Upload a GPX file of waypoints
2. Click on a waypoint to see its position on the map
3. Drag a waypoint marker on the map to adjust its position
4. Save your changes
5. Enter an address and rank waypoints by distance from address


Dependencies
------------
* `GeoDjango <http://geodjango.org>`_ (see :doc:`geodjango-install`)
* `Google Maps API Key <http://code.google.com/apis/maps/signup.html>`_
* `jQuery <http://jquery.com>`_
* `Firebug <http://getfirebug.com>`_


Walkthrough
-----------

.. _geodjango-patch:

Patch GeoDjango
^^^^^^^^^^^^^^^^^^^^^^
Depending on your version of Django, you may have to patch some of the
Django code.  Specifically, you may have to edit `base.py` in GeoDjango's
GDAL wrapper so that it handles long pointers on 64-bit systems.

Old `django/contrib/gis/gdal/base.py`
::

    def _set_ptr(self, ptr):
        # Only allow the pointer to be set with pointers of the
        # compatible type or None (NULL).
        if isinstance(ptr, int):
            self._ptr = self.ptr_type(ptr)
        elif isinstance(ptr, (self.ptr_type, NoneType)):
            self._ptr = ptr
        else:
            raise TypeError('Incompatible pointer type')


New `django/contrib/gis/gdal/base.py`
::

    def _set_ptr(self, ptr):
        # Only allow the pointer to be set with pointers of the
        # compatible type or None (NULL).
        if isinstance(ptr, int) or isinstance(ptr, long):
            self._ptr = self.ptr_type(ptr)
        elif isinstance(ptr, (self.ptr_type, NoneType)):
            self._ptr = ptr
        else:
            raise TypeError('Incompatible pointer type')

Thanks to Ronald Kemker for the patch and thanks to Justin Bronn for closing the ticket: http://code.djangoproject.com/ticket/11609



Create spatial database
^^^^^^^^^^^^^^^^^^^^^^^
If you are using the default PostgreSQL configuration, then you 
need to have a PostgreSQL account with the same name as your Linux 
account; see :ref:`postgresql-default`
::

    su - postgres
    createuser YOUR-USERNAME
    createdb -T template_postgis -O YOUR-USERNAME geodjango-googlemaps
    exit

If you are using the alternate PostgreSQL configuration, then 
you can set postgres to be the owner of the database, although this 
is less secure; see :ref:`postgresql-alternate`
::

    su - postgres
    createdb -T template_postgis -O postgres geodjango-googlemaps
    exit


Create GeoDjango project
^^^^^^^^^^^^^^^^^^^^^^^^
Start a new project and an application
::

    django-admin.py startproject application
    cd application
    python manage.py startapp waypoints


Configure settings
""""""""""""""""""
Add the following lines to the top of ``settings.py``
::

    # Import system modules
    import os
    # Set paths
    baseDirectory = os.path.dirname(__file__)
    fillPath = lambda x: os.path.join(baseDirectory, x)
    staticPath, templatePath = map(fillPath, ['static', 'templates'])

Change the following parameters in ``settings.py`` as indicated
::

    MEDIA_ROOT = staticPath
    MEDIA_URL = '/static/'
    TEMPLATE_DIRS = (
        templatePath,
    )
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.admin',
        'django.contrib.gis',
        'application.waypoints',
    )

Set your database connection parameters in ``settings.py`` according 
to your PostgreSQL configuration
::

    DATABASE_ENGINE = 'postgresql_psycopg2'
    DATABASE_NAME = geodjango-googlemaps

    # Default PostgreSQL configuration
    DATABASE_USER = YOUR-USERNAME
    DATABASE_PASSWORD = YOUR-PASSWORD
    
    # Alternate PostgreSQL configuration
    DATABASE_USER = postgres
    DATABASE_PASSWORD = YOUR-POSTGRES-PASSWORD

Create subfolders in the project folder ``application``
::
    
    mkdir static templates templates/waypoints

Place a copy of the `jQuery <http://jquery.com>`_ library in the ``static`` folder
::

    cd static
    wget http://jqueryjs.googlecode.com/files/jquery-1.3.2.min.js
    cd ..


Configure models
""""""""""""""""
Edit ``waypoints/models.py``; the *geometry* attribute contains the geospatial information and uses the 4326 spatial reference system that is compatible with the longitude and latitude coordinates provided by the Google Maps API.
::

    # Import geodjango modules
    from django.contrib.gis.db import models


    class Waypoint(models.Model):

        name = models.CharField(max_length=32)
        geometry = models.PointField(srid=4326)
        objects = models.GeoManager()

        def __unicode__(self):
            return '%s %s %s' % (self.name, self.geometry.x, self.geometry.y)

Create tables
::

    python manage.py syncdb



Configure urls
""""""""""""""
Edit ``urls.py``; the code at the end enables ``python manage.py runserver`` to serve static files as described in `How to serve static files <http://docs.djangoproject.com/en/dev/howto/static-files>`_
::

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
        mediaURL = settings.MEDIA_URL[1:]
        # Extend
        urlpatterns += patterns('',
            (r'^%s(?P<path>.*)$' % mediaURL, 'django.views.static.serve', 
                {'document_root': settings.MEDIA_ROOT}),
        )


Create ``waypoints/urls.py`` and add the following code
::

    # Import django modules
    from django.conf.urls.defaults import *


    urlpatterns = patterns('application.waypoints.views',
        url(r'^$', 'index', name='waypoints-index'),
    )

Test
""""
Edit ``waypoints/views.py`` and add the following code
::
    
    from django.http import HttpResponse


    def index(request):
        return HttpResponse('Hello')

Run development server
::

    python manage.py runserver

Go to http://localhost:8000

.. image:: images/geodjango-googlemaps-project-create.png


View map
^^^^^^^^
Create url
""""""""""
Make sure that ``waypoints/urls.py`` has an index
::

    # Import django modules
    from django.conf.urls.defaults import *


    urlpatterns = patterns('application.waypoints.views',
        url(r'^$', 'index', name='waypoints-index'),
    )

Create template
"""""""""""""""
Create the template ``templates/waypoints/index.html``
::

    <!doctype html>
    <html>
    <head>
    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=x">
    </script>
    <script>
    var map;
    function initialize() {
        if (GBrowserIsCompatible()) {
            map = new GMap2(document.getElementById('map'));
            map.setCenter(new GLatLng(41.879535, -87.624333), 5);
            map.setUIToDefault();
        }
    }
    </script>
    <style>
        body {
            font-family: sans-serif;
        }
        #map {
            width: 500px; 
            height: 300px;
        }
    </style>
    </head>
    <body onload="initialize()" onunload="GUnload()">
        <div id=map></div>
    </body>
    </html>


Create view
"""""""""""
Edit ``waypoints/views.py``
::

    from django.shortcuts import render_to_response
    
    def index(request):
        return render_to_response('waypoints/index.html', {
        })

Test
""""
Run development server
::

    python manage.py runserver

Go to http://localhost:8000

.. image:: images/geodjango-googlemaps-map-view.png


View waypoints
^^^^^^^^^^^^^^
Modify template
"""""""""""""""
Add a script link to the `jQuery <http://jquery.com>`_ library below the script link to the Google Maps API in ``templates/waypoints/index.html``
::

    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=x">
    </script>
    <script src="/static/jquery-1.3.2.min.js"></script>

Add Javascript code for displaying waypoint markers
::

    <script>
    var waypointByID = {};
    {% for waypoint in waypoints %}
    waypointByID[{{waypoint.id}}] = {
        name: "{{waypoint.name}}", 
        lat: {{waypoint.geometry.y}}, 
        lng: {{waypoint.geometry.x}}
    };
    {% endfor %}
    var marker;
        
    $(document).ready(function () {
        function activate_waypoints() {
            // Add waypoint click handler
            $('.waypoint').each(function () {
                $(this).click(function() {
                    var waypoint = waypointByID[this.id];
                    var center = new GLatLng(waypoint.lat, waypoint.lng);
                    if (marker) map.removeOverlay(marker);
                    marker = new GMarker(center);
                    map.addOverlay(marker);
                    map.panTo(center);
                }).hover(
                    function () {this.className = this.className.replace('OFF', 'ON');}, 
                    function () {this.className = this.className.replace('ON', 'OFF');}
                );
            });
        }
        activate_waypoints();
    });
    </script>

Add styles for the waypoint content box
::

    <style>
        #waypoints {
            overflow: auto;
            width: 500px;
            height: 100px;
        }
        .linkOFF {color: darkblue} 
        .linkON {color: white; background-color: darkblue}
    </style>

Finally, add the waypoint content box in the body
::

    <div id=waypoints>
        {{content}}
    </div>

Your ``templates/waypoints/index.html`` template should resemble the following
::

    <!doctype html>
    <html>
    <head>
    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=x"></script>
    <script src="/static/jquery-1.3.2.min.js"></script>
    <script>
    var waypointByID = {};
    {% for waypoint in waypoints %}
    waypointByID[{{waypoint.id}}] = {
        name: "{{waypoint.name}}", 
        lat: {{waypoint.geometry.y}}, 
        lng: {{waypoint.geometry.x}}
    };
    {% endfor %}
    var map, marker;
    function initialize() {
        if (GBrowserIsCompatible()) {
            map = new GMap2(document.getElementById('map'));
            map.setCenter(new GLatLng(41.879535, -87.624333), 5);
            map.setUIToDefault();
        }
        $(document).ready(function () {
            function activate_waypoints() {
                // Add waypoint click handler
                $('.waypoint').each(function () {
                    $(this).click(function() {
                        var waypoint = waypointByID[this.id];
                        var center = new GLatLng(waypoint.lat, waypoint.lng);
                        if (marker) map.removeOverlay(marker);
                        marker = new GMarker(center);
                        map.addOverlay(marker);
                        map.panTo(center);
                    }).hover(
                        function () {this.className = this.className.replace('OFF', 'ON');}, 
                        function () {this.className = this.className.replace('ON', 'OFF');}
                    );
                });
            }
            activate_waypoints();
        });
    }
    </script>
    <style>
        body {
            font-family: sans-serif;
        }
        #map {
            width: 500px; 
            height: 300px;
        }
        #waypoints {
            overflow: auto;
            width: 500px;
            height: 100px;
        }
        .linkOFF {color: darkblue} 
        .linkON {color: white; background-color: darkblue}
    </style>
    </head>
    <body onload="initialize()" onunload="GUnload()">
        <div id=map></div>
        <div id=waypoints>
            {{content}}
        </div>
    </body>
    </html>

Create another template for displaying waypoint content in ``templates/waypoints/waypoints.html``
::

    {% for waypoint in waypoints %}
        <div id={{waypoint.id}} class='waypoint linkOFF'>
            {{waypoint.name}} ({{waypoint.geometry.y}}, {{waypoint.geometry.x}})
        </div>
    {% endfor %}


Modify view
"""""""""""
Modify *index* in ``waypoints/views.py``
::

    # Import django modules
    from django.shortcuts import render_to_response
    from django.template.loader import render_to_string
    # Import custom modules
    from application.waypoints.models import Waypoint

    def index(request):
        waypoints = Waypoint.objects.all()
        return render_to_response('waypoints/index.html', {
            'waypoints': waypoints,
            'content': render_to_string('waypoints/waypoints.html', {'waypoints': waypoints}),
        })


Test
""""
Create data
::
    
    from waypoints.models import Waypoint
    Waypoint(name='New York', geometry='POINT(-73.9869510 40.7560540)').save()
    Waypoint(name='Buenos Aires', geometry='POINT(-58.4173090 -34.6117810)').save()
    Waypoint(name='Moscow', geometry='POINT(37.6176330 55.7557860)').save()
    Waypoint(name='Atlanta', geometry='POINT(-84.3896630 33.7544870)').save()
    print Waypoint.objects.all()

Run development server
::

    python manage.py runserver

Go to http://localhost:8000 and click on a waypoint in the content box

.. image:: images/geodjango-googlemaps-waypoints-view.png


Edit waypoints
^^^^^^^^^^^^^^
Create url
""""""""""
Add *save* to ``waypoints/urls.py``
::

    # Import django modules
    from django.conf.urls.defaults import *


    urlpatterns = patterns('application.waypoints.views',
        url(r'^$', 'index', name='waypoints-index'),
        url(r'^save$', 'save', name='waypoints-save'),
    )

Modify template
"""""""""""""""
Update jQuery's ``$(document).ready()`` construct in ``templates/waypoints/index.html``
::

    var current_object;

    $(document).ready(function () {
        function activate_waypoints() {
            // Add waypoint click handler
            $('.waypoint').each(function () {
                $(this).click(function() {
                    var waypoint = waypointByID[this.id];
                    var center = new GLatLng(waypoint.lat, waypoint.lng);
                    current_object = $(this);
                    if (marker) map.removeOverlay(marker);
                    marker = new GMarker(center, {draggable: true});
                    GEvent.addListener(marker, "dragend", function() {
                        var latlng = marker.getLatLng();
                        waypoint.lat = latlng.lat();
                        waypoint.lng = latlng.lng();
                        current_object.html(waypoint.name + 
                            ' (' + waypoint.lat + 
                            ', ' + waypoint.lng + ')');
                        $('#button_save').removeAttr("disabled");
                    });
                    map.addOverlay(marker);
                    map.panTo(center);
                }).hover(
                    function () {this.className = this.className.replace('OFF', 'ON');}, 
                    function () {this.className = this.className.replace('ON', 'OFF');}
                );
            });
        }
        $('#button_save').click(function () {
            var waypointStrings = [];
            for (id in waypointByID) {
                waypoint = waypointByID[id];
                waypointStrings.push(id + ' ' + waypoint.lng + ' ' + waypoint.lat);
            };
            $.post("{% url waypoints-save %}", 
                {waypoints_payload: waypointStrings.join('\n')}, function (data) {
                    $('#button_save').attr("disabled","disabled");
                });
        });
        activate_waypoints();
    });

Add a button to the body
::

    <div id=waypoints>
        {{content}}
    </div>
    <button id=button_save disabled=disabled>Save</button>


Create view
"""""""""""
Add *save* to ``waypoints/views.py``
::

    from django.http import HttpResponse
    from application.waypoints.models import Waypoint

    def save(request):
        for waypointString in request.POST['waypoints_payload'].splitlines():
            waypointID, waypointX, waypointY = waypointString.split()
            waypoint = Waypoint.objects.get(id=int(waypointID))
            waypoint.geometry.set_x(float(waypointX))
            waypoint.geometry.set_y(float(waypointY))
            waypoint.save()
        return HttpResponse('ok')

Test
""""
Run development server
::

    python manage.py runserver

Go to http://localhost:8000, drag a waypoint to a new location and save

.. image:: images/geodjango-googlemaps-waypoints-save.png

Rank waypoints by distance from address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create url
""""""""""
Add *search* to ``waypoints/urls.py``
::

    # Import django modules
    from django.conf.urls.defaults import *


    urlpatterns = patterns('application.waypoints.views',
        url(r'^$', 'index', name='waypoints-index'),
        url(r'^save$', 'save', name='waypoints-save'),
        url(r'^search$', 'search', name='waypoints-search'),
    )

Modify template
"""""""""""""""
Add a geocoder to ``templates/waypoints/index.html``
::

    var map, marker, geocoder, current_object;
        
    function initialize() {
        if (GBrowserIsCompatible()) {
            map = new GMap2(document.getElementById('map'));
            map.setCenter(new GLatLng(41.879535, -87.624333), 5);
            map.setUIToDefault();
            geocoder = new GClientGeocoder();
        }

Insert the following code within jQuery's ``$(document).ready()`` construct
::

    $('#button_search').click(function () {
        var searchString = $('#input_search').val();
        geocoder.getLatLng(searchString, function(result) {
            if (!result) {
                alert("Could not find geocoordinates for your address query");
            } else {
                $.get("{% url waypoints-search %}", 
                    {lat: result.lat(), lng: result.lng()}, function (data) {
                        $('#waypoints').html(data.content);
                        waypointByID = data.waypointByID;
                        activate_waypoints();
                    }, 'json');
            }
        });
    });

Add a *search* button to the body after the *save* button
::

    <input id=input_search value="Chicago, IL"> 
    <input type=button 
        value='Rank waypoints by distance from address' 
        id=button_search>

Create view
"""""""""""
Add *search* to ``waypoints/views.py``
::

    from django.contrib.gis.geos import Point
    import simplejson

    def search(request):
        # Build searchPoint
        searchPoint = Point(float(request.GET['lng']), float(request.GET['lat']))
        # Search database
        waypoints = Waypoint.objects.distance(searchPoint).order_by('distance')
        waypointByID = dict((x.id, {
            'name': x.name, 
            'lat': x.geometry.y, 
            'lng': x.geometry.x
        }) for x in waypoints)
        json = {
            'content': render_to_string('waypoints/waypoints.html', {
                'waypoints': waypoints
            }),
            'waypointByID': waypointByID,
        }
        # Return
        return HttpResponse(simplejson.dumps(json))

Test
""""
Run development server
::

    python manage.py runserver

Go to http://localhost:8000, type an address and rank by distance from address

.. image:: images/geodjango-googlemaps-waypoints-search.png



Upload waypoints from GPX file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create url
""""""""""
Add *upload* to ``waypoints/urls.py``
::

    # Import django modules
    from django.conf.urls.defaults import *


    urlpatterns = patterns('application.waypoints.views',
        url(r'^$', 'index', name='waypoints-index'),
        url(r'^save$', 'save', name='waypoints-save'),
        url(r'^search$', 'search', name='waypoints-search')
        url(r'^upload$', 'upload', name='waypoints-upload'),
    )

Create template
"""""""""""""""
Add the *upload* form above the map in ``templates/waypoints/index.html``
::

    <form enctype="multipart/form-data" method=post action="{% url waypoints-upload %}">
        <input type=file name=gpx>
        <input type=submit value='Upload GPX'>
    </form>

Create view
"""""""""""
Add *upload* view in ``waypoints/views.py``
::
    
    from django.http import HttpResponseRedirect
    from django.contrib.gis.gdal import DataSource
    from django.core.urlresolvers import reverse
    import itertools
    import tempfile
    import os
    from application.waypoints.models import Waypoint
    from application import settings

    def upload(request):
        # If the form contains an upload,
        if 'gpx' in request.FILES:
            # Get
            gpxFile = request.FILES['gpx']
            # Save
            targetPath = tempfile.mkstemp()[1]
            destination = open(targetPath, 'wt')
            for chunk in gpxFile.chunks(): 
                destination.write(chunk)
            destination.close()
            # Parse
            dataSource = DataSource(targetPath)
            layer = dataSource[0]
            waypointNames = layer.get_fields('name')
            waypointGeometries = layer.get_geoms()
            for waypointName, waypointGeometry in itertools.izip(waypointNames, waypointGeometries):
                waypoint = Waypoint(name=waypointName, geometry=waypointGeometry.wkt)
                waypoint.save()
            # Clean up
            os.remove(targetPath)
        # Redirect
        return HttpResponseRedirect(reverse('waypoints-index'))

Test
""""
Run development server
::

    python manage.py runserver

Go to http://localhost:8000 and upload a GPX file such as the `New Zealand Tourist Waypoints <http://www.esnips.com/web/GPSStuff>`_

.. image:: images/geodjango-googlemaps-waypoints-upload.png


Troubleshooting
---------------

Google Maps
^^^^^^^^^^^

Google Maps hangs
"""""""""""""""""
Google Maps occasionally hangs after a redirect when Firebug is enabled.  Disabling Firebug or restarting your browser will resolve this problem.

Google Maps API key is invalid
""""""""""""""""""""""""""""""
Google Maps may indicate that your API key is invalid.  Make sure that you have replaced the value of the *sensor* parameter to either *true* or *false* and that there are no line breaks in the URL. 

Incorrect
::

    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=true_or_false
    &amp;key=x"
    type="text/javascript">
    </script>

Correct
::

    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=x">
    </script>
