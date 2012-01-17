'Save and load points to a shapefile'
# Import system modules
import osgeo.ogr
import osgeo.osr
import os


# Core

def save(shapePath, geoLocations, proj4):
    'Save points in the given shapePath'
    # Get driver
    driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
    # Create shapeData
    shapePath = validateShapePath(shapePath)
    if os.path.exists(shapePath): 
        os.remove(shapePath)
    shapeData = driver.CreateDataSource(shapePath)
    # Create spatialReference
    spatialReference = getSpatialReferenceFromProj4(proj4)
    # Create layer
    layerName = os.path.splitext(os.path.split(shapePath)[1])[0]
    layer = shapeData.CreateLayer(layerName, spatialReference, osgeo.ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()
    # For each point,
    for pointIndex, geoLocation in enumerate(geoLocations):
        # Create point
        geometry = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        geometry.SetPoint(0, geoLocation[0], geoLocation[1])
        # Create feature
        feature = osgeo.ogr.Feature(layerDefinition)
        feature.SetGeometry(geometry)
        feature.SetFID(pointIndex)
        # Save feature
        layer.CreateFeature(feature)
        # Cleanup
        geometry.Destroy()
        feature.Destroy()
    # Cleanup
    shapeData.Destroy()
    # Return
    return shapePath

def load(shapePath):
    'Given a shapePath, return a list of points in GIS coordinates'
    # Open shapeData
    shapeData = osgeo.ogr.Open(validateShapePath(shapePath))
    # Validate shapeData
    validateShapeData(shapeData)
    # Get the first layer
    layer = shapeData.GetLayer()
    # Initialize
    points = []
    # For each point,
    for index in xrange(layer.GetFeatureCount()):
        # Get
        feature = layer.GetFeature(index)
        geometry = feature.GetGeometryRef()
        # Make sure that it is a point
        if geometry.GetGeometryType() != osgeo.ogr.wkbPoint: 
            raise ShapeDataError('This module can only load points; use geometry_store.py')
        # Get pointCoordinates
        pointCoordinates = geometry.GetX(), geometry.GetY()
        # Append
        points.append(pointCoordinates)
        # Cleanup
        feature.Destroy()
    # Get spatial reference as proj4
    proj4 = layer.GetSpatialRef().ExportToProj4()
    # Cleanup
    shapeData.Destroy()
    # Return
    return points, proj4

def merge(sourcePaths, targetPath):
    'Merge a list of shapefiles into a single shapefile'
    # Load
    items = [load(validateShapePath(x)) for x in sourcePaths]
    pointLists = [x[0] for x in items]
    points = reduce(lambda x,y: x+y, pointLists)
    spatialReferences= [x[1] for x in items]
    # Make sure that all the spatial references are the same
    if len(set(spatialReferences)) != 1: 
        raise ShapeDataError('The shapefiles must have the same spatial reference')
    spatialReference = spatialReferences[0]
    # Save
    save(validateShapePath(targetPath), points, spatialReference)

def getSpatialReferenceFromProj4(proj4):
    'Return GDAL spatial reference object from proj4 string'
    spatialReference = osgeo.osr.SpatialReference()
    spatialReference.ImportFromProj4(proj4)
    return spatialReference


# Validate

def validateShapePath(shapePath):
    'Validate shapefile extension'
    return os.path.splitext(str(shapePath))[0] + '.shp'

def validateShapeData(shapeData):
    'Make sure we can access the shapefile'
    # Make sure the shapefile exists
    if not shapeData:
        raise ShapeDataError('The shapefile is invalid')
    # Make sure there is exactly one layer
    if shapeData.GetLayerCount() != 1:
        raise ShapeDataError('The shapefile must have exactly one layer')


# Error

class ShapeDataError(Exception):
    pass
