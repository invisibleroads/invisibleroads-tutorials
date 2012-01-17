'Tests for geometry_store'
# Import system modules
import os
import shutil
import itertools
import tempfile
import datetime
import unittest
from osgeo import ogr
from shapely import geometry
# Import custom modules
import geometry_store


# Define constants

shapelyGeometries = [
    geometry.Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]),
    geometry.Polygon([(10, 0), (10, 10), (20, 10), (20, 0), (10, 0)]),
]
fieldPacks = [
    ('xxx', 11111, 44444.44, datetime.date(1939, 9, 1)),
    ('yyy', 22222, 88888.88, datetime.date(1950, 6, 25)),
]
fieldDefinitions = [
    ('Name', ogr.OFTString),
    ('Population', ogr.OFTInteger),
    ('GDP', ogr.OFTReal),
    ('Updated', ogr.OFTDate),
]


# Define tests

class TestGeometryStore(unittest.TestCase):
    'Demonstrate geometry_store usage'

    index = 0

    def setUp(self):
        self.temporaryFolder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temporaryFolder)

    def getPath(self, fileExtension):
        'Return a path with the given fileExtension in temporaryFolder'
        self.index += 1
        return os.path.join(self.temporaryFolder, str(self.index) + fileExtension)

    def test(self):
        'Run tests'

        print 'Save and load a SHP file without attributes'
        path = self.getPath('.shp')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries)
        result = geometry_store.load(path)
        self.assertEqual(result[0].strip(), geometry_store.proj4LL)
        self.assertEqual(len(result[1]), len(shapelyGeometries))

        print 'Save and load a SHP file with attributes'
        path = self.getPath('.shp')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, fieldPacks, fieldDefinitions)
        result = geometry_store.load(path)
        self.assertEqual(len(result[2]), len(fieldPacks))
        for shapelyGeometry, fieldPack in itertools.izip(result[1], result[2]):
            print
            for fieldValue, (fieldName, fieldType) in itertools.izip(fieldPack, result[3]):
                print '%s = %s' % (fieldName, fieldValue)
            print shapelyGeometry

        print 'Save a SHP file with attributes with different targetProj4'
        path = self.getPath('.shp')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, fieldPacks, fieldDefinitions, targetProj4=geometry_store.proj4SM)
        result = geometry_store.load(path)
        self.assertNotEqual(result[0].strip(), geometry_store.proj4LL)

        print 'Load a SHP file with attributes with different targetProj4'
        path = self.getPath('.shp')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, fieldPacks, fieldDefinitions)
        result = geometry_store.load(path, targetProj4=geometry_store.proj4SM)
        self.assertNotEqual(result[0].strip(), geometry_store.proj4LL)

        print 'Save and load a ZIP file without attributes using save'
        path = self.getPath('.shp.zip')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries)
        result = geometry_store.load(path)
        self.assertEqual(result[0].strip(), geometry_store.proj4LL)
        self.assertEqual(len(result[1]), len(shapelyGeometries))

        print 'Save and load a ZIP file with attributes using save'
        path = self.getPath('.shp.zip')
        geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, fieldPacks, fieldDefinitions)
        result = geometry_store.load(path)
        self.assertEqual(len(result[2]), len(fieldPacks))

        print 'Test saving and loading ZIP files of point coordinates'
        path = self.getPath('.shp.zip')
        geometry_store.save_points(path, geometry_store.proj4LL, [(0, 0)], fieldPacks, fieldDefinitions)
        result = geometry_store.load_points(path)
        self.assertEqual(result[1], [(0, 0)])

        print 'Test get_transform_point'
        transform_point0 = geometry_store.get_transform_point(geometry_store.proj4LL, geometry_store.proj4LL)
        transform_point1 = geometry_store.get_transform_point(geometry_store.proj4LL, geometry_store.proj4SM)
        self.assertNotEqual(transform_point0(0, 0), transform_point1(0, 0))

        print 'Test get_transform_geometry'
        transform_geometry = geometry_store.get_transform_geometry(geometry_store.proj4LL, geometry_store.proj4SM)
        self.assertEqual(type(transform_geometry(geometry.Point(0, 0))), type(geometry.Point(0, 0)))
        self.assertEqual(type(transform_geometry(ogr.CreateGeometryFromWkt('POINT (0 0)'))), type(ogr.CreateGeometryFromWkt('POINT (0 0)')))

        print 'Test get_coordinateTransformation'
        geometry_store.get_coordinateTransformation(geometry_store.proj4LL, geometry_store.proj4SM)

        print 'Test get_spatialReference'
        geometry_store.get_spatialReference(geometry_store.proj4LL)
        with self.assertRaises(geometry_store.GeometryError):
            geometry_store.get_spatialReference('')

        print 'Test get_geometryType'
        geometry_store.get_geometryType(shapelyGeometries)

        print 'Test save() when a fieldPack has fewer fields than definitions'
        with self.assertRaises(geometry_store.GeometryError):
            path = self.getPath('.shp')
            geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, [x[1:] for x in fieldPacks], fieldDefinitions)

        print 'Test save() when a fieldPack has more fields than definitions'
        with self.assertRaises(geometry_store.GeometryError):
            path = self.getPath('.shp')
            geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, [x * 2 for x in fieldPacks], fieldDefinitions)

        print 'Test save() when the driverName is unrecognized'
        with self.assertRaises(geometry_store.GeometryError):
            path = self.getPath('.shp')
            geometry_store.save(path, geometry_store.proj4LL, shapelyGeometries, driverName='')

        print 'Test load() when format is unrecognized'
        with self.assertRaises(geometry_store.GeometryError):
            path = self.getPath('')
            geometry_store.load(path)
