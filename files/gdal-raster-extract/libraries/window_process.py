# Import system modules
# Import custom modules
import sample_store
import view


def extract(targetDatasetPath, label, windowGeoLength, multispectralImage, panchromaticImage, geoCenters):
    # Initialize
    dataset = sample_store.create(targetDatasetPath)
    windowCount = len(geoCenters)
    # For each geoCenter,
    for windowIndex, geoCenter in enumerate(geoCenters):
        window = [x.extractCenteredGeoWindow(geoCenter, windowGeoLength, windowGeoLength) for x in multispectralImage, panchromaticImage]
        if window[0] and window[1]: dataset.addSample(label, geoCenter, *window)
        if windowIndex % 100 == 0: 
            view.printPercentUpdate(windowIndex + 1, windowCount)
    view.printPercentFinal(windowCount)
    # Return
    return dataset
