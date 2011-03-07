"""
ZipFile wrapper for reading and writing to ZIP files.
"""
# Import system modules
import os
import shutil
import zipfile
import tempfile
from decorator import decorator


# Define core

@decorator
def save(function, *args, **kwargs):
    """
    Decorator to support saving to ZIP files

    If the first argument has a ZIP extension, it runs the function on the 
    first argument minus the ZIP extension and compresses the resulting files.
    """
    # Get targetExtension
    targetPath = kwargs.get('targetPath', args[0])
    targetBase, targetExtension = os.path.splitext(targetPath)
    # If the targetPath does not have a ZIP extension,
    if targetExtension.lower() != '.zip':
        # Run function as usual
        return function(*args, **kwargs)
    # Make temporaryFolder
    with TemporaryFolder() as temporaryFolder:
        # Run function in temporaryFolder
        temporaryPath = os.path.join(temporaryFolder, os.path.basename(targetBase))
        functionResult = function(temporaryPath, *args[1:], **kwargs)
        # Make zipFile
        with zipfile.ZipFile(targetPath, 'w', zipfile.ZIP_DEFLATED) as zipFile:
            # Walk sourceFolderPath
            for rootPath, directories, fileNames in os.walk(temporaryFolder):
                # For each file,
                for fileName in fileNames:
                    filePath = os.path.join(rootPath, fileName)
                    relativePath = filePath[len(temporaryFolder) + 1:]
                    zipFile.write(filePath, relativePath, zipfile.ZIP_DEFLATED)
        # Return
        return targetPath

@decorator
def load(function, *args, **kwargs):
    """
    Decorator to support loading from ZIP files

    If the first argument has a ZIP extension, it uncompresses the 
    first argument and runs the function on the resulting files.
    """
    # Get sourceExtension
    sourcePath = kwargs.get('sourcePath', args[0])
    sourceBase, sourceExtension = os.path.splitext(sourcePath)
    # If the sourcePath does not have a ZIP extension,
    if sourceExtension.lower() != '.zip':
        # Run function as usual
        return function(*args, **kwargs)
    # Make temporaryFolder
    with TemporaryFolder() as temporaryFolder:
        # Open zipFile
        with zipfile.ZipFile(sourcePath) as zipFile:
            # Unzip to temporaryFolder
            zipFile.extractall(temporaryFolder)
            # Run function on extracted files and exit on first success
            errors = []
            for fileName in zipFile.namelist():
                try:
                    temporaryPath = os.path.join(temporaryFolder, fileName)
                    return function(temporaryPath, *args[1:], **kwargs)
                except Exception, error:
                    errors.append(str(error))
            else:
                raise ZipError('Could not run {} on any file in {}:\n{}'.format(
                    function,
                    sourcePath,
                    '\n'.join(errors),
                ))


# Define wrappers

class TemporaryFolder(object):

    def __init__(self, suffix='', prefix='tmp', dir=None):
        self.suffix = suffix
        self.prefix = prefix
        self.dir = dir

    def __enter__(self):
        self.temporaryFolder = tempfile.mkdtemp(self.suffix, self.prefix, self.dir)
        return self.temporaryFolder

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.temporaryFolder)


# Define errors

class ZipError(object):
    pass
