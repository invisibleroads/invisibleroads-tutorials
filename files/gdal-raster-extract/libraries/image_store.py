# Import system modules
import osgeo.gdal
import osgeo.osr
import struct
import numpy
import Image
import cPickle as pickle
import cStringIO as StringIO
# Import custom modules
import store
import view


# Types used by struct.unpack
typeByGDT = {
    osgeo.gdal.GDT_Byte: 'B',
    osgeo.gdal.GDT_UInt16: 'H', 
}
modeByType = {
    osgeo.gdal.GDT_Byte: 'L',
    osgeo.gdal.GDT_UInt16: 'I;16', 
}


# Define shortcuts

def load(imagePath): 
    return GeoImage(imagePath)

def convertGeoDimensionsToPixelDimensions(geoWidth, geoHeight, geoTransform):
    g0, g1, g2, g3, g4, g5 = geoTransform
    return int(round(abs(float(geoWidth) / g1))), int(round(abs(float(geoHeight) / g5)))

def convertPixelLocationsToGeoLocations(pixelLocations, geoTransform):
    return [convertPixelLocationToGeoLocation(x, geoTransform) for x in pixelLocations]

def convertPixelLocationToGeoLocation(pixelLocation, geoTransform):
    g0, g1, g2, g3, g4, g5 = geoTransform
    xPixel, yPixel = pixelLocation
    xGeo = g0 + xPixel*g1 + yPixel*g2
    yGeo = g3 + xPixel*g4 + yPixel*g5
    return xGeo, yGeo


# Define core

class GeoImage(object):

    # Constructor

    def __init__(self, imagePath):
        # Initialize
        self.imagePath = imagePath
        self.dataset = osgeo.gdal.Open(imagePath)
        self.width = self.dataset.RasterXSize
        self.height = self.dataset.RasterYSize
        self.geoTransform = self.dataset.GetGeoTransform()
        # Get spatialReference
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromWkt(self.dataset.GetProjectionRef())
        self.spatialReferenceAsProj4 = spatialReference.ExportToProj4()

    # Get

    def getPath(self):
        return self.imagePath

    def getPixelWidth(self):
        return self.width

    def getPixelHeight(self):
        return self.height

    def getGeoTransform(self):
        return self.geoTransform

    def getSpatialReference(self):
        return self.spatialReferenceAsProj4

    # Extract

    def extractCenteredGeoWindow(self, geoCenter, geoWidth, geoHeight):
        pixelCenter = self.convertGeoLocationToPixelLocation(geoCenter)
        pixelWidth, pixelHeight = self.convertGeoDimensionsToPixelDimensions(geoWidth, geoHeight)
        return self.extractCenteredPixelWindow(pixelCenter, pixelWidth, pixelHeight)

    def extractCenteredPixelWindow(self, pixelCenter, pixelWidth, pixelHeight):
        pixelUpperLeft = centerPixelFrame(pixelCenter, pixelWidth, pixelHeight)[:2]
        return self.extractPixelWindow(pixelUpperLeft, pixelWidth, pixelHeight)

    def extractPixelWindow(self, pixelUpperLeft, pixelWidth, pixelHeight):
        # Set
        iLeft = int(pixelUpperLeft[0])
        iTop = int(pixelUpperLeft[1])
        iWidth = int(pixelWidth)
        iHeight = int(pixelHeight)
        # If the box is outside, return
        if not self.isWindowInside(iLeft, iTop, iWidth, iHeight): return
        # Extract
        bands = map(self.dataset.GetRasterBand, xrange(1, self.dataset.RasterCount + 1))
        packs = [(x.DataType, x.ReadRaster(iLeft, iTop, iWidth, iHeight)) for x in bands]
        # Return
        return Window(iLeft, iTop, iWidth, iHeight, packs)

    # Is

    def isWindowInside(self, left, top, width, height):
        right = left + width
        bottom = top + height
        if left >= 0 and top >= 0 and right <= self.width and bottom <= self.height: return True

    # Convert

    def convertGeoFrameToPixelFrame(self, geoFrame):
        geoLeft, geoTop, geoRight, geoBottom = geoFrame
        pixelLeft, pixelTop = self.convertGeoLocationToPixelLocation((geoLeft, geoTop))
        pixelRight, pixelBottom = self.convertGeoLocationToPixelLocation((geoRight, geoBottom))
        pixelLeft, pixelRight = sorted((pixelLeft, pixelRight))
        pixelTop, pixelBottom = sorted((pixelTop, pixelBottom))
        return pixelLeft, pixelTop, pixelRight, pixelBottom

    def convertPixelFrameToGeoFrame(self, pixelFrame):
        pixelLeft, pixelTop, pixelRight, pixelBottom = pixelFrame
        geoLeft, geoTop = self.convertPixelLocationToGeoLocation((pixelLeft, pixelTop))
        geoRight, geoBottom = self.convertPixelLocationToGeoLocation((pixelRight, pixelBottom))
        geoLeft, geoRight = sorted((geoLeft, geoRight))
        geoTop, geoBottom = sorted((geoTop, geoBottom))
        return geoLeft, geoTop, geoRight, geoBottom

    def convertGeoLocationToPixelLocation(self, geoLocation):
        g0, g1, g2, g3, g4, g5 = self.geoTransform
        xGeo, yGeo = geoLocation
        if g2 == 0:
            xPixel = (xGeo - g0) / float(g1)
            yPixel = (yGeo - g3 - xPixel*g4) / float(g5)
        else:
            xPixel = (yGeo*g2 - xGeo*g5 + g0*g5 - g2*g3) / float(g2*g4 - g1*g5)
            yPixel = (xGeo - g0 - xPixel*g1) / float(g2)
        return int(round(xPixel)), int(round(yPixel))

    def convertPixelLocationToGeoLocation(self, pixelLocation):
        return convertPixelLocationToGeoLocation(pixelLocation, self.geoTransform)

    def convertGeoLocationsToPixelLocations(self, geoLocations):
        return map(self.convertGeoLocationToPixelLocation, geoLocations)

    def convertPixelLocationsToGeoLocations(self, pixelLocations):
        return map(self.convertPixelLocationToGeoLocation, pixelLocations)

    def convertGeoDimensionsToPixelDimensions(self, geoWidth, geoHeight):
        return convertGeoDimensionsToPixelDimensions(geoWidth, geoHeight, self.geoTransform)

    def convertPixelDimensionsToGeoDimensions(self, pixelWidth, pixelHeight):
        g0, g1, g2, g3, g4, g5 = self.geoTransform
        return abs(pixelWidth * g1), abs(pixelHeight * g5)


class Window(object):

    values = None
    matrices = None
    matrixImages = None, None
    pairwiseMatrices = None
    images_pil = None
    images_pylab = None, None
    
    def __init__(self, left, top, width, height, packs):
        # Set
        self.width = width
        self.height = height
        self.packs = packs
        # Initialize
        self.frame = left, top, left + width, top + height

    def getFrame(self):
        return self.frame

    def getValues(self):
        if not self.values:
            length = self.width * self.height
            self.values = [struct.unpack('%d%s' % (length, typeByGDT[x[0]]), x[1]) for x in self.packs]
        return self.values

    def getMatrices(self):
        if not self.matrices:
            self.matrices = [numpy.reshape(x, (self.height, self.width)) for x in self.getValues()]
        return self.matrices

    def getMatrixImages(self, imageWidthInPixels, imageHeightInPixels):
        imageDimensions = imageWidthInPixels, imageHeightInPixels
        if not self.matrixImages[0] or self.matrixImages[1] != imageDimensions:
            self.matrixImages = getImages_pylab('matshow', self.getMatrices(), *imageDimensions), imageDimensions
        return self.matrixImages[0]

    def getImages_pil(self):
        if not self.images_pil:
            imageDimensions = self.width, self.height
            self.images_pil = [Image.fromstring(modeByType[x[0]], imageDimensions, x[1]) for x in self.packs]
        return self.images_pil

    def getImages_pylab(self, imageWidthInPixels, imageHeightInPixels):
        imageDimensions = imageWidthInPixels, imageHeightInPixels
        if not self.images_pylab[0] or self.images_pylab[1] != imageDimensions:
            self.images_pylab = getImages_pylab('imshow', self.getMatrices(), *imageDimensions), imageDimensions
        return self.images_pylab[0]

    def pickle(self):
        return pickle.dumps((self.width, self.height, self.packs))


def unpickle(data):
    if not data: return None
    width, height, packs = pickle.loads(data)
    return Window(0, 0, width, height, packs)


# Get helpers

def centerPixelFrame(pixelCenter, pixelWidth, pixelHeight):
    # Compute frame
    pixelLeft = pixelCenter[0] - pixelWidth / 2
    pixelTop = pixelCenter[1] - pixelHeight / 2
    pixelRight = pixelLeft + pixelWidth
    pixelBottom = pixelTop + pixelHeight
    # Return
    return pixelLeft, pixelTop, pixelRight, pixelBottom

def getCenter(frame):
    left, top, right, bottom = frame
    widthHalved = (right - left) / 2
    heightHalved = (bottom - top) / 2
    return int(left + widthHalved), int(top + heightHalved)

def getWindowCenter(windowLocation, windowPixelWidth, windowPixelHeight):
    left, top = windowLocation
    widthHalved = windowPixelWidth / 2
    heightHalved = windowPixelHeight / 2
    return int(left + widthHalved), int(top + heightHalved)

def getPixelsInFrame(frame):
    left, top, right, bottom = frame
    xRange = xrange(left, right)
    yRange = xrange(top, bottom)
    return [(x, y) for x in xRange for y in yRange]

def getImages_pylab(string_method, matrices, imageWidthInPixels, imageHeightInPixels):
    # Import system modules
    import matplotlib
    import pylab
    # Initialize
    images = []
    convertPixelLengthToInchLength = lambda x: x / float(matplotlib.rc_params()['figure.dpi'])
    imageWidthInInches = convertPixelLengthToInchLength(imageWidthInPixels)
    imageHeightInInches = convertPixelLengthToInchLength(imageHeightInPixels)
    imageDimensions = imageWidthInInches, imageHeightInInches
    # For each matrix,
    for matrix in matrices:
        # Create a new figure
        pylab.figure(figsize=imageDimensions)
        axes = pylab.axes()
        # Plot grayscale matrix
        method = getattr(axes, string_method)
        method(matrix, cmap=pylab.cm.gray)
        # Clear tick marks
        axes.set_xticks([])
        axes.set_yticks([])
        # Save image
        imageFile = StringIO.StringIO()
        pylab.savefig(imageFile, format='png')
        imageFile.seek(0)
        # Append
        images.append(Image.open(imageFile))
    # Return
    return images


class Information(object):

    # Constructor

    def __init__(self, informationPath):
        self.information = store.loadInformation(informationPath)

    # Positive location

    def getPositiveLocationPath(self):
        return self.information['positive location']['path']

    # Multispectral

    def getMultispectralImagePath(self):
        return self.information['multispectral image']['path']

    def getMultispectralImage(self):
        return load(self.getMultispectralImagePath())

    # Panchromatic

    def getPanchromaticImagePath(self):
        return self.information['panchromatic image']['path']

    def getPanchromaticImage(self):
        return load(self.getPanchromaticImagePath())
