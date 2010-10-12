# Import system modules
import numpy


def makeSampleLabelPaths(basePath):
    return basePath + '-samples', basePath + '-labels'

def makeLabelGeneratorFromLushDataset(filePath):
    # Set paths
    labelPath = makeSampleLabelPaths(filePath)[1]
    # Initialize
    labelFile = open(labelPath)
    header = labelFile.next()
    terms = []
    # For each line,
    for line in labelFile:
        # Extend terms
        terms.extend(int(x) for x in line.split())
        # Pop each term
        for termIndex in xrange(len(terms)):
            yield terms.pop(0)

def makeSampleGeneratorFromLushDataset(filePath):
    # Set paths
    samplePath = makeSampleLabelPaths(filePath)[0]
    # Initialize
    sampleFile = open(samplePath)
    header = sampleFile.next()
    sampleShape = [int(x) for x in header.split()[3:]]
    sampleSize = numpy.product(sampleShape)
    terms = []
    # For each line,
    for line in sampleFile:
        # Extend terms
        terms.extend(float(x) for x in line.split())
        # If we have enough terms,
        while len(terms) >= sampleSize:
            # Yield sample
            yield numpy.array(terms[:sampleSize]).reshape(sampleShape)
            # Set terms
            terms = terms[sampleSize:]
