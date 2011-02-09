"""
GDAL wrapper for reading and writing geospatial data 
to a variety of vector formats.

For a list of supported vector formats and driver names,
please see http://www.gdal.org/ogr/ogr_formats.html
"""
# Import system modules
import os
import itertools
from osgeo import ogr, osr
from shapely import wkb, geometry


# Set constants
proj4LL = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
proj4SM = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs'


# Define shortcuts

def savePoints(targetPath, proj4, coordinateTuples, fieldPacks=None, fieldDefinitions=None, driverName='ESRI Shapefile'):
    return save(targetPath, proj4, [geometry.Point(x) for x in coordinateTuples], fieldPacks, fieldDefinitions, driverName)

def loadPoints(targetPath):
    proj4, shapelyGeometries, fieldPacks, fieldDefinitions = load(targetPath)
    return proj4, [(point.x, point.y) for point in shapelyGeometries], fieldPacks, fieldDefinitions


# Define core

def save(targetPath, proj4, shapelyGeometries, fieldPacks=None, fieldDefinitions=None, driverName='ESRI Shapefile'):
    'Save shapelyGeometries using the given proj4 and fields'
    # Validate arguments
    if not fieldPacks:
        fieldPacks = []
    if not fieldDefinitions:
        fieldDefinitions = []
    if fieldPacks and set(len(x) for x in fieldPacks) != set([len(fieldDefinitions)]):
        raise GeometryError('A field definition is required for each field')
    # Create dataSource
    if os.path.exists(targetPath): 
        os.remove(targetPath)
    dataSource = ogr.GetDriverByName(driverName).CreateDataSource(targetPath)
    # Determine geometry type for layer
    geometryTypes = list(set(type(x) for x in shapelyGeometries))
    geometryType = ogr.wkbUnknown if len(geometryTypes) > 1 else {
        geometry.Point: ogr.wkbPoint,
        geometry.point.PointAdapter: ogr.wkbPoint,
        geometry.LineString: ogr.wkbLineString,
        geometry.linestring.LineStringAdapter: ogr.wkbLineString,
        geometry.Polygon: ogr.wkbPolygon,
        geometry.polygon.PolygonAdapter: ogr.wkbPolygon,
        geometry.MultiPoint: ogr.wkbMultiPoint,
        geometry.multipoint.MultiPointAdapter: ogr.wkbMultiPoint,
        geometry.MultiLineString: ogr.wkbMultiLineString,
        geometry.multilinestring.MultiLineStringAdapter: ogr.wkbMultiLineString,
        geometry.MultiPolygon: ogr.wkbMultiPolygon,
        geometry.multipolygon.MultiPolygonAdapter: ogr.wkbMultiPolygon,
    }[geometryTypes[0]]
    # Create layer
    spatialReference = osr.SpatialReference()
    spatialReference.ImportFromProj4(proj4)
    layer = dataSource.CreateLayer(os.path.splitext(os.path.basename(targetPath))[0], spatialReference, geometryType)
    # Create fields
    for fieldName, fieldType in fieldDefinitions:
        layer.CreateField(ogr.FieldDefn(fieldName, fieldType))
    featureDefinition = layer.GetLayerDefn()
    # For each geometry,
    for shapelyGeometry, fieldPack in itertools.izip(shapelyGeometries, fieldPacks) if fieldPacks else ((x, []) for x in shapelyGeometries):
        # Create feature
        feature = ogr.Feature(featureDefinition)
        feature.SetGeometry(ogr.CreateGeometryFromWkb(shapelyGeometry.wkb))
        for fieldIndex, fieldValue in enumerate(fieldPack):
            feature.SetField(fieldIndex, fieldValue)
        # Save feature
        layer.CreateFeature(feature)
        feature.Destroy()
    # Return
    return targetPath

def load(sourcePath):
    'Load proj4, shapelyGeometries, fields'
    # Initialize
    shapelyGeometries, fieldPacks, fieldDefinitions = [], [], []
    # Prepare
    dataSource = ogr.Open(sourcePath)
    layer = dataSource.GetLayer()
    featureDefinition = layer.GetLayerDefn()
    fieldIndices = xrange(featureDefinition.GetFieldCount())
    for fieldIndex in fieldIndices:
        fieldDefinition = featureDefinition.GetFieldDefn(fieldIndex)
        fieldDefinitions.append((fieldDefinition.GetName(), fieldDefinition.GetType()))
    feature = layer.GetNextFeature()
    # While there are more features,
    while feature:
        # Append
        shapelyGeometries.append(wkb.loads(feature.GetGeometryRef().ExportToWkb()))
        fieldPacks.append([feature.GetField(x) for x in fieldIndices])
        # Get the next feature
        feature = layer.GetNextFeature()
    # Load
    spatialReference = layer.GetSpatialRef()
    proj4 = spatialReference.ExportToProj4() if spatialReference else ''
    # Return
    return proj4, shapelyGeometries, fieldPacks, fieldDefinitions

def getTransformPoint(sourceProj4, targetProj4=proj4LL):
    'Return a function that transforms coordinates from one spatial reference to another'
    if sourceProj4 == targetProj4:
        return lambda x, y: (x, y)
    sourceSRS = osr.SpatialReference()
    sourceSRS.ImportFromProj4(sourceProj4)
    targetSRS = osr.SpatialReference()
    targetSRS.ImportFromProj4(targetProj4)
    return lambda x, y: osr.CoordinateTransformation(sourceSRS, targetSRS).TransformPoint(x, y)[:2]


# Define errors

class GeometryError(Exception):
    pass
