Convert a document to PDF using the Adobe Acrobat COM interface
===============================================================
We first presented this material as part of a three-hour session on `Automating Windows Applications using win32com <http://us.pycon.org/2008/tutorials/AutomatingWindows>`_ during the `2008 Python Conference <http://us.pycon.org/2008>`_ in Chicago, Illinois.


Requirements
------------
* `Adobe Acrobat <http://www.adobe.com/products/acrobat>`_
* `Python <http://python.org>`_
* `Python for Windows extensions <http://sourceforge.net/projects/pywin32>`_


Convert an HTML document to PDF
-------------------------------
Here we use Adobe Acrobat to save an HTML document in PDF format.  Please note that this is for illustrative purposes only and is not the most efficient way to generate a PDF document.
::

    # Import system modules
    import os
    import win32com.client
    import win32com.client.makepy

    # Generate type library so that we can access constants
    win32com.client.makepy.GenerateFromTypeLibSpec('Acrobat')

    def convertHTML2PDF(htmlPath, pdfPath):
        'Convert an HTML document to PDF format'
        # Connect to Adobe Acrobat
        avDoc = win32com.client.Dispatch('AcroExch.AVDoc')
        # Open HTML document
        avDoc.Open(os.path.abspath(htmlPath), 'html2pdf')
        # Save in PDF format
        pdDoc = avDoc.GetPDDoc()
        pdDoc.Save(win32com.client.constants.PDSaveFull, os.path.abspath(pdfPath))
        pdDoc.Close()
        # Close HTML document without prompting to save
        avDoc.Close(True)


Links
-----
* `DjVu <http://en.wikipedia.org/wiki/DjVu>`_ is a file format that generally produces significantly smaller files than PDF, especially for image-heavy documents.
