# Import system modules
import random
import numpy


def uniquify(sequence):
    seen = set()
    return [x for x in sequence if x not in seen and not seen.add(x)]


def cut(sequence, fraction, withRandomization=True):
    # Copy
    sequence = list(sequence)
    # Randomize
    if withRandomization: random.shuffle(sequence)
    # Count
    totalCount = len(sequence)
    partialCount = int(numpy.ceil(totalCount * fraction))
    # Split
    for firstIndex in xrange(0, totalCount, partialCount):
        lastIndex = firstIndex + partialCount
        insideFraction = sequence[firstIndex:lastIndex]
        outsideFraction = sequence[0:firstIndex] + sequence[lastIndex:totalCount]
        yield outsideFraction, insideFraction
