# Import system modules
import xapian
import re


class TextMachine(object):
    """
    Simplified formatting class for extracting and highlighting parts of
    a document that match a search query.
    """

    def __init__(self, extractLength=None, highlightTemplate=None, joinText=' ... '):
        self.extractLength = extractLength
        self.highlightTemplate = highlightTemplate
        self.joinText = joinText

    def process(self, queryString, content):
        # Parse query
        queryParser = xapian.QueryParser()
        queryParser.set_stemmer(xapian.Stem('english'))
        queryParser.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
        query = queryParser.parse_query(queryString)
        # Parse content after replacing non-alphanumeric characters with spaces
        queryParser.parse_query(re.sub('\W', ' ', content).lower())
        # Create search pattern
        documentTerms = sum([list(queryParser.unstemlist(x)) for x in set(query)], [])
        if not documentTerms:
            documentTerms = set(query)
        pattern = re.compile(r'\b(%s)\b' % '|'.join(re.escape(x) for x in documentTerms), re.IGNORECASE)
        # If the user does not want to extract text or there is no queryString,
        if not self.extractLength or not queryString:
            extract = content
        # If the user wants to extract text and there is a queryString,
        else:
            # Initialize
            extractIntervals = []
            extractLengthHalved = self.extractLength / 2
            # For each matchInterval,
            for match in pattern.finditer(content):
                # Prepare
                mStart = max(0, match.start() - extractLengthHalved)
                mEnd = min(len(content), match.end() + extractLengthHalved)
                # Absorb it
                absorbInterval((mStart, mEnd), extractIntervals)
            # Load extracts
            extract = self.joinText.join(content[eStart:eEnd].strip() for eStart, eEnd in extractIntervals)
        # If the user wants to highlight relevant terms and there is a queryString,
        if self.highlightTemplate and queryString:
            extract = pattern.sub(self.highlightTemplate % r'\1', extract)
        # Return
        return extract


def absorbInterval((mStart, mEnd), extractIntervals):
    'Merge overlapping intervals'
    # For each extractInterval,
    for eIndex, (eStart, eEnd) in enumerate(extractIntervals):
        # If the matchInterval is contained in an existing extractInterval,
        if eStart <= mStart and eEnd >= mEnd:
            # Ignore it because we have it already
            return
        # If the matchInterval overlaps the left side of extractInterval,
        elif mEnd > eStart and mEnd < eEnd:
            # Extend the extractInterval in that direction
            extractIntervals[eIndex] = mStart, eEnd
            return
        # If the matchInterval overlaps the right side of extractInterval,
        elif mStart > eStart and mStart < eEnd:
            # Extend the extractInterval in that direction
            extractIntervals[eIndex] = eStart, mEnd
            return
    # The matchInterval does not overlap any existing extractInterval
    extractIntervals.append((mStart, mEnd))
