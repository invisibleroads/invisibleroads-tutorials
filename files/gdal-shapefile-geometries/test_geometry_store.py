'Tests for geometry_store'
# Import system modules
import os
import shutil
import itertools
import tempfile
import datetime
from osgeo import ogr
from shapely import geometry
# Import custom modules
import geometry_store


def test_geometry_store():
    'Demonstrate geometry_store usage'
    # Create temporary folder
    temporaryFolder = tempfile.mkdtemp()
    # Set targetPath
    targetPath = os.path.join(temporaryFolder, 'xxx.shp')
    # Save
    geometry_store.save(targetPath, geometry_store.proj4LL, [
        geometry.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]),
        geometry.Polygon([(10, 0), (10, 10), (20, 10), (20, 0), (10, 0)]),
    ], [
        ('World War II', 11111, 44444.44, datetime.date(1939, 9, 1)),
        ('Korean War', 22222, 88888.88, datetime.date(1950, 6, 25)),
    ], [
        ('Name', ogr.OFTString),
        ('Population', ogr.OFTInteger),
        ('GDP', ogr.OFTReal),
        ('Updated', ogr.OFTDate),
    ])
    # Load
    proj4, shapelyGeometries, fieldPacks, fieldDefinitions = geometry_store.load(targetPath)
    # Display
    for shapelyGeometry, fieldPack in itertools.izip(shapelyGeometries, fieldPacks):
        print
        for fieldValue, (fieldName, fieldType) in itertools.izip(fieldPack, fieldDefinitions):
            print '%s = %s' % (fieldName, fieldValue)
        print shapelyGeometry
    # Remove temporary folder
    shutil.rmtree(temporaryFolder)
