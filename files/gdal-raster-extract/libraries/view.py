# Import system modules
import sys


# Feedback

def printDirectly(feedback):
    sys.stdout.write(feedback)
    sys.stdout.flush()

def printPercentUpdate(currentCount, totalCount):
    printDirectly('\r% 3d %% \t%d        ' % (100 * currentCount / totalCount, currentCount))

def printPercentFinal(totalCount):
    printDirectly('\r100 %% \t%d        \n' % totalCount)

def trackProgress(generator, totalCount, packetLength):
    # Initialize
    items = []
    # For each item,
    for currentCount, item in enumerate(generator):
        items.append(item)
        if currentCount % packetLength == 0: 
            printPercentUpdate(currentCount + 1, totalCount)
    # Return
    printPercentFinal(totalCount)
    return items
