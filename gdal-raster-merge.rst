Merge rasters into a single raster with GDAL
============================================
Sometimes it is necessary to merge multiple GeoTIFFs into a single raster.  For example, if the image you are trying to :doc:`orthorectify <envi-image-orthorectify>` overlaps multiple disjoint `SRTM DEM <http://srtm.csi.cgiar.org>`_ GeoTIFFs, then you can combine the `SRTM DEM <http://srtm.csi.cgiar.org>`_ GeoTIFFs into a single image using the `gdal_merge.py <http://gdal.org/gdal_merge.html>`_ script available with the `GDAL <http://gdal.org>`_ package.


Requirements
------------
* `Geospatial Data Abstraction Library <http://gdal.org>`_


Usage
-----
The `gdal_merge.py <http://gdal.org/gdal_merge.html>`_ script takes the paths of the GeoTIFFs you want to combine as input and creates a single GeoTIFF as output.  If you do not specify a filename with the ``-o`` option, the script will save the result as ``out.tif``.
::

    gdal_merge.py image1.tif image2.tif -o merged.tif
