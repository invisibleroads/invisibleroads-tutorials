#!/usr/bin/env python


# Import system modules
import optparse
# Import custom modules
from libraries import image_store, point_store, window_process


# If we are running the script from the command-line,
if __name__ == '__main__':
    # Parse options and arguments
    optionParser = optparse.OptionParser(
        usage='%prog MULTISPECTRAL-PATH PANCHROMATIC-PATH SHAPE-PATH',
        epilog=(
            'Extracts raster windows from MULTISPECTRAL-PATH and '
            'PANCHROMATIC-PATH using locations from SHAPE-PATH and '
            'saves results in OUTPUT-PATH.'
        )
    )
    optionParser.add_option('-o', '--output-path', dest='outputPath', 
        metavar='OUTPUT-PATH', default='samples.db',
        help='save results in OUTPUT-PATH')
    optionParser.add_option('-m', '--meters', dest='windowGeoLength', 
        metavar='LENGTH', default=25, type='int',
        help='specify centered window length in meters')
    optionParser.add_option('-l', '--label', dest='windowLabel', 
        metavar='INTEGER', default=1, type='int',
        help='specify window label')
    options, arguments = optionParser.parse_args()
    # Verify
    if len(arguments) == 3:
        # Extract
        multispectralImagePath, panchromaticImagePath, locationPath = arguments
        window_process.extract(options.outputPath, 
            options.windowLabel, options.windowGeoLength,
            image_store.load(multispectralImagePath), 
            image_store.load(panchromaticImagePath),
            point_store.load(locationPath)[0])
    else:
        # Show help
        optionParser.print_help()
