Save points to a shapefile with GDAL
====================================
Save point coordinates and their spatial reference to a shapefile.  This tutorial was first presented as part of a three-hour session on `Working with Geographic Information Systems in Python <http://us.pycon.org/2009/tutorials/schedule/1PM4/>`_ during the `2009 Python Conference <http://us.pycon.org/2009/>`_ in Chicago, Illinois.

.. raw:: html

    <object width="425" height="344"><param name="movie" value="http://www.youtube.com/v/BieCLKuoQEA&hl=en&fs=1&rel=0"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/BieCLKuoQEA&hl=en&fs=1&rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="425" height="344"></embed></object>


Requirements
------------
* `Python <http://python.org>`_ 
* `Geospatial Data Abstraction Library <http://gdal.org>`_

For the walkthrough, you will also need the following:

* `IPython <http://ipython.scipy.org/>`_


Example
-------
Download the :download:`code and data <files/gdal-shapefile-points.zip>`, unzip and start Python.
::

    wget http://invisibleroads.com/tutorials/_downloads/gdal-shapefile-points.zip
    unzip gdal-shapefile-points.zip
    cd gdal-shapefile-points
    python

Save points and spatial reference.
::

    import point_store
    point_store.save('points-shifted.shp', [
        (474595, 4429281), 
        (474580, 4429137), 
        (474499, 4429249),
    ], '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')


Concepts
--------
* A point is a type of geometry stored as a feature.
* A layer can have many features.
* A datasource can have many layers.
* The driver saves the datasource in a specific format.
* `GDAL has drivers for different formats <http://gdal.org/ogr/ogr_formats.html>`_.

::

    Driver
        Datasource
            Layer
                Feature
                    Geometry
                        Point
        

Walkthrough
-----------
Import GDAL.
::

    import osgeo.ogr, osgeo.osr

Set spatial reference.
::

    spatialReference = osgeo.osr.SpatialReference()
    spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')

Create shapefile.
::
    
    driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
    shapeData = driver.CreateDataSource('points-shifted.shp')

Create layer.
::

    layer = shapeData.CreateLayer('layer1', spatialReference, osgeo.ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()

Create point.
::

    point = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
    point.SetPoint(0, 474595, 4429281)

Put point as a geometry inside a feature.
::

    featureIndex = 0
    feature = osgeo.ogr.Feature(layerDefinition)
    feature.SetGeometry(point)
    feature.SetFID(featureIndex)

Put feature in a layer.
::

    layer.CreateFeature(feature)

Flush.
::

    shapeData.Destroy()

You can peek at the contents of the shapefile using `Quantum GIS <http://qgis.org/>`_.


Code
-------
.. literalinclude:: files/gdal-shapefile-points/point_store.py
