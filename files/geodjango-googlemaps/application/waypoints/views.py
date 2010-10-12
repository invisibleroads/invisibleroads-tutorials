# Import django modules
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
# Import geodjango modules
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
# Import system modules
import os
import tempfile
import itertools
import simplejson
# Import custom modules
from application import settings
from application.waypoints.models import Waypoint


def index(request):
    waypoints = Waypoint.objects.all()
    return render_to_response('waypoints/index.html', {
        'waypoints': waypoints,
        'content': render_to_string('waypoints/waypoints.html', {'waypoints': waypoints}),
    })


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


def search(request):
    # Build searchPoint
    searchPoint = Point(float(request.GET['lng']), float(request.GET['lat']))
    # Search database
    waypoints = Waypoint.objects.distance(searchPoint).order_by('distance')
    waypointByID = dict((x.id, {'name': x.name, 'lat': x.geometry.y, 'lng': x.geometry.x}) for x in waypoints)
    json = {
        'content': render_to_string('waypoints/waypoints.html', {'waypoints': waypoints}),
        'waypointByID': waypointByID,
    }
    # Return
    return HttpResponse(simplejson.dumps(json))


def save(request):
    for waypointString in request.POST['waypoints_payload'].splitlines():
        waypointID, waypointX, waypointY = waypointString.split()
        waypoint = Waypoint.objects.get(id=int(waypointID))
        waypoint.geometry.set_x(float(waypointX))
        waypoint.geometry.set_y(float(waypointY))
        waypoint.save()
    return HttpResponse('ok')
