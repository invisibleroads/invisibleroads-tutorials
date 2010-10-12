# Import system modules
import osgeo.ogr
import osgeo.osr
import os


# Core

def load(shapePath):
    """Given a shapePath, return a list of points in GIS coordinates."""
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
        # Get feature
        feature = layer.GetFeature(index)
        # Get pointObject
        geometry = feature.GetGeometryRef()
        # Make sure that it is a point
        if geometry.GetGeometryType() != osgeo.ogr.wkbPoint: 
            raise ShapeDataError(x_wrongGeometryType)
        # Get pointCoordinates
        pointCoordinates = geometry.GetX(), geometry.GetY()
        # Append
        points.append(pointCoordinates)
    # Return
    return points, layer.GetSpatialRef().ExportToProj4()

def save(shapePath, geoLocations, spatialReferenceAsProj4):
    """Save points in the given shapePath."""
    # Get driver
    driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
    # Create shapeData
    shapePath = validateShapePath(shapePath)
    if os.path.exists(shapePath): os.remove(shapePath)
    shapeData = driver.CreateDataSource(shapePath)
    # Create spatialReference
    spatialReference = getSpatialReferenceFromProj4(spatialReferenceAsProj4)
    # Create layer
    layerName = os.path.splitext(os.path.split(shapePath)[1])[0]
    layer = shapeData.CreateLayer(layerName, spatialReference, osgeo.ogr.wkbPoint)
    layerDefinition = layer.GetLayerDefn()
    # For each point,
    for pointIndex, geoLocation in enumerate(geoLocations):
        # Create point
        point = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        point.SetPoint(0, geoLocation[0], geoLocation[1])
        # Create feature
        feature = osgeo.ogr.Feature(layerDefinition)
        feature.SetGeometry(point)
        feature.SetFID(pointIndex)
        # Save feature
        layer.CreateFeature(feature)
    # Return
    return shapePath

def merge(sourcePaths, targetPath):
    # Load
    items = [load(validateShapePath(x)) for x in sourcePaths]
    pointLists = [x[0] for x in items]
    points = reduce(lambda x,y: x+y, pointLists)
    spatialReferences= [x[1] for x in items]
    # Make sure that all the spatial references are the same
    if len(set(spatialReferences)) != 1: 
        raise ShapeDataError(x_differentSpatialReferences)
    spatialReference = spatialReferences[0]
    # Save
    save(validateShapePath(targetPath), points, spatialReference)

def getSpatialReferenceFromProj4(spatialReferenceAsProj4):
    spatialReference = osgeo.osr.SpatialReference()
    spatialReference.ImportFromProj4(spatialReferenceAsProj4)
    return spatialReference


# Validate

def validateShapePath(shapePath):
    return os.path.splitext(str(shapePath))[0] + '.shp'

def validateShapeData(shapeData):
    # Make sure the shapefile exists
    if not shapeData: raise ShapeDataError(x_badPath)
    # Make sure there is exactly one layer
    if shapeData.GetLayerCount() != 1: raise ShapeDataError(x_wrongLayerCount)


# Error

class ShapeDataError(Exception):
    def __init__(self, code): self.code = code
    def __str__(self): return messagePackByCode[self.code][0]
    def getMessagePack(self): return messagePackByCode[self.code]

x_badPath, x_wrongLayerCount, x_wrongGeometryType, x_differentSpatialReferences = xrange(4)

messagePackByCode = {
    x_badPath: (
        'The shapefile is invalid.',
        'Bad path',
    ),
    x_wrongLayerCount: (
        'The shapefile must have exactly one layer.',
        'Wrong number of layers',
    ),
    x_wrongGeometryType: (
        'The shapefile must contain only points.',
        'Wrong geometry',
    ),
    x_differentSpatialReferences: (
        'The shapefiles must have the same spatial reference.',
        'Different spatial references',
    ),
}
