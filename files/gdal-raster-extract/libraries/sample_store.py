# Import system modules
import sqlite3
import os
import numpy
import random
import scipy.io
import itertools
import cPickle as pickle
# Import custom modules
import view
import store
import image_store
import sequence


# Set SQL
sql_getSample = 'SELECT hasRoof, xGeo, yGeo, multispectralData, panchromaticData FROM samples'


# Shortcuts

def create(datasetPath):
    datasetPath = store.replaceFileExtension(datasetPath, 'db')
    if os.path.exists(datasetPath): os.remove(datasetPath)
    return Store(datasetPath)

def load(datasetPath):
    datasetPath = store.replaceFileExtension(datasetPath, 'db')
    if not os.path.exists(datasetPath): raise IOError('Dataset does not exist: ' + datasetPath)
    return Store(datasetPath)


# Restore

def restoreResult(result):
    # Extract
    hasRoof, xGeo, yGeo, multispectralData, panchromaticData = result
    geoCenter = xGeo, yGeo
    # Restore
    multispectralWindow = image_store.unpickle(multispectralData)
    panchromaticWindow = image_store.unpickle(panchromaticData)
    # Return
    return hasRoof, geoCenter, multispectralWindow, panchromaticWindow


class Store(object):

    # Constructor

    def __init__(self, datasetPath):
        # Fix extension
        datasetPath = store.replaceFileExtension(datasetPath, 'db')
        # Check whether the dataset exists
        flag_exists = True if os.path.exists(datasetPath) else False
        # Connect
        self.connection = sqlite3.connect(datasetPath)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # If the dataset doesn't exist, create it
        if not flag_exists: 
            self.cursor.execute('CREATE TABLE samples (hasRoof INTEGER, xGeo REAL, yGeo REAL, multispectralData BLOB, panchromaticData BLOB)')
            self.connection.commit()
        # Remember
        self.datasetPath = datasetPath
    
    # Destructor

    def __del__(self):
        self.connection.close()

    # Add

    @store.commit
    def addSample(self, hasRoof, geoCenter, multispectralWindow, panchromaticWindow):
        xGeo, yGeo = geoCenter
        multispectralData = multispectralWindow.pickle()
        panchromaticData = panchromaticWindow.pickle()
        return 'INSERT INTO samples (hasRoof, xGeo, yGeo, multispectralData, panchromaticData) VALUES (?,?,?,?,?)', (hasRoof, xGeo, yGeo, multispectralData, panchromaticData)

    # Delete

    @store.commit
    def deleteSample(self, sampleID):
        return 'DELETE FROM samples WHERE rowid=?', [sampleID]

    # Get

    def getDatasetPath(self): 
        return self.datasetPath
    
    @store.fetchAll
    def getSampleIDs(self):
        return 'SELECT rowid FROM samples', None, store.pullFirst

    @store.fetchAll
    def getRandomSampleIDs(self):
        return 'SELECT rowid FROM samples ORDER BY RANDOM()', None, store.pullFirst

    @store.fetchAll
    def getPositiveSampleIDs(self):
        return 'SELECT rowid FROM samples WHERE hasRoof=1', None, store.pullFirst

    @store.fetchAll
    def getNegativeSampleIDs(self):
        return 'SELECT rowid FROM samples WHERE hasRoof=0', None, store.pullFirst

    @store.fetchAll
    def getSamplesByIDs(self, sampleIDs):
        return sql_getSample + ' WHERE samples.rowID IN (%s)' % ','.join(map(str, sampleIDs)), None, restoreResult

    @store.fetchAll
    def getSamples(self):
        return sql_getSample, None, restoreResult

    @store.fetchOne
    def getSample(self, sampleID):
        return sql_getSample + ' WHERE samples.rowID=?', (sampleID,), restoreResult

    @store.fetchAll
    def getGeoCenters(self):
        return 'SELECT xGeo, yGeo FROM samples', None

    # Count

    @store.fetchOne
    def countSamples(self):
        return 'SELECT COUNT(*) FROM samples', None, store.pullFirst

    @store.fetchOne
    def countPositiveSamples(self):
        return 'SELECT COUNT(*) FROM samples WHERE hasRoof=1', None, store.pullFirst

    @store.fetchOne
    def countNegativeSamples(self):
        return 'SELECT COUNT(*) FROM samples WHERE hasRoof=0', None, store.pullFirst

    def getStatistics(self):
        return {
            'total': self.countSamples(),
            'positive': self.countPositiveSamples(),
            'negative': self.countNegativeSamples(),
        }

    # Cut

    def cutIDs(self, testFraction, withRandomization=True):
        # For each cut,
        for cutPack in sequence.cut(self.getSampleIDs(), testFraction, withRandomization):
            # Yield
            yield cutPack

    # Save

    def saveForMatlab(self, targetPath):
        # Initialize
        samples = self.getSamples(); labels = []; geoCenters = []
        reds = []; greens = []; blues = []; infrareds = []; panchromatics = []
        # Assemble
        for index in xrange(len(samples)):
            # Extract
            hasRoof, geoCenter, multispectralWindow, panchromaticWindow = samples[index]
            # Gather
            labels.append(hasRoof); geoCenters.append(geoCenter)
            # Gather multispectral
            red, green, blue, infrared = multispectralWindow.getMatrices()
            reds.append(red); greens.append(green); blues.append(blue); infrareds.append(infrared)
            # Gather panchromatic 
            panchromatics.append(panchromaticWindow.getMatrices()[0])
        # Save
        matrixDictionary = {
            'labels': numpy.dstack(labels), 'geoCenters': numpy.dstack(geoCenters),
            'reds': numpy.dstack(reds), 'greens': numpy.dstack(greens),
            'blues': numpy.dstack(blues), 'infrareds': numpy.dstack(infrareds),
            'panchromatics': numpy.dstack(panchromatics),
        }
        scipy.io.savemat(targetPath, matrixDictionary, True)


# Save

def save(targetPath, datasetSampleIDs):
    # Open targetDataset
    targetDataset = Store(targetPath)
    # Save samples
    sampleCount = len(datasetSampleIDs)
    for sampleIndex, (sourceDataset, sampleID) in enumerate(datasetSampleIDs):
        targetDataset.addSample(*sourceDataset.getSample(sampleID))
        if sampleIndex % 100 == 0: 
            view.printPercentUpdate(sampleIndex + 1, sampleCount)
    view.printPercentFinal(sampleCount)
    # Return
    return targetDataset
