Save and load geometries and fields from a shapefile with GDAL
==============================================================
Here we demonstrate the use of a GDAL wrapper for processing geometries such as points, lines, polygons and their associated fields, properties, attributes.

* Save geometries with their associated fields to SHP, KML, GPX files.
* Load geometries with their associated fields from SHP, KML, GPX files.

`See the complete table of vector formats supported by GDAL <http://gdal.org/ogr/ogr_formats.html>`_.  Driver names are listed in the column entitled *Code*.


Requirements
------------
* `Python <http://python.org>`_ 
* `IPython <http://ipython.scipy.org/>`_
* `Shapely <http://trac.gispython.org/lab/wiki/Shapely>`_
* `Geospatial Data Abstraction Library <http://gdal.org>`_


Example
-------
Download the :download:`code <files/gdal-shapefile-geometries.zip>`, unzip and start IPython.
::

    wget http://invisibleroads.com/tutorials/_downloads/gdal-shapefile-geometries.zip
    unzip gdal-shapefile-geometries.zip
    cd gdal-shapefile-geometries
    ipython

Import modules.
::

    # Import system modules
    import itertools
    import osgeo.ogr
    import shapely.geometry
    # Import custom modules
    import geometry_store

Use shortcut to save points in GPX format for use with GPS devices.
::

    geometry_store.savePoints('villages.gpx', geometry_store.proj4LL, [(0, 0), (1, 1)], driverName='GPX')

Save lines with fields as a KML file using the Spherical Mercator spatial reference.
::

    geometry_store.save('roads.kml', geometry_store.proj4SM, [
        shapely.geometry.LineString([(0, 5), (5, 0)]),
        shapely.geometry.LineString([(5, 0), (10, 0)]),
        shapely.geometry.LineString([(10, 0), (10, 5)]),
    ], [
        ('Left road', 1980),
        ('Middle road', 1985),
        ('Right road', 1995),
    ], [
        ('Name', osgeo.ogr.OFTString),
        ('Year', osgeo.ogr.OFTInteger),
    ], driverName='KML')

Save polygons with fields.
::

    geometry_store.save('geometries.shp', geometry_store.proj4LL, [
        shapely.geometry.Polygon([(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]),
        shapely.geometry.MultiPolygon([
            (((0, 0), (0, 3), (3, 3), (3, 0)), [((0, 0), (0, 2), (2, 2), (2, 0))]),
        ]),
    ], [
        ('Area depicted by Polygon', 10000),
        ('Areas depicted by MultiPolygon', 20000),
    ], [
        ('Summary', osgeo.ogr.OFTString),
        ('Cost', osgeo.ogr.OFTReal),
    ])

Load geometries with fields.
::

    # Load
    proj4, shapelyGeometries, fieldPacks, fieldDefinitions = geometry_store.load('geometries.shp')
    # Display
    for shapelyGeometry, fieldPack in itertools.izip(shapelyGeometries, fieldPacks):
        print
        for fieldValue, (fieldName, fieldType) in itertools.izip(fieldPack, fieldDefinitions):
            print '%s = %s' % (fieldName, fieldValue)
        print shapelyGeometry


Code
----
.. literalinclude:: files/gdal-shapefile-geometries/test_geometry_store.py

.. literalinclude:: files/gdal-shapefile-geometries/geometry_store.py
