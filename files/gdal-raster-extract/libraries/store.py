# Import system modules
import os
import re
import sys
import time
import numpy
import datetime
import ConfigParser


# SQL

def execute(function, args, kwargs):
    # Extract
    self = args[0]
    # Execute
    z = function(*args, **kwargs)
    sql, value = z[:2]
    if value == None: self.cursor.execute(sql)
    else: self.cursor.execute(sql, value)
    # Return
    method = z[2] if len(z) > 2 else None
    return self, method

def commit(function):
    def wrapper(*args, **kwargs):
        self = execute(function, args, kwargs)[0]
        self.connection.commit()
        return self.cursor.lastrowid
    return wrapper

def fetchOne(function):
    def wrapper(*args, **kwargs):
        self, method = execute(function, args, kwargs)
        result = self.cursor.fetchone()
        return method(result) if method else result
    return wrapper

def fetchAll(function):
    def wrapper(*args, **kwargs):
        self, method = execute(function, args, kwargs)
        results = self.cursor.fetchall()
        return map(method, results) if method else results
    return wrapper

def pullFirst(result):
    if result != None: return result[0]

def pullTrueIfResult(result):
    return True if result != None else False


# File 

def replaceFileExtension(filePath, newExtension):
    if not newExtension.startswith('.'): newExtension = '.' + newExtension
    base = os.path.splitext(filePath)[0]
    return base + newExtension

def extractFileBaseName(filePath):
    filename = os.path.split(filePath)[1]
    return os.path.splitext(filename)[0]

def extractFileName(filePath):
    return os.path.split(filePath)[1]

def verifyPath(filePath):
    if not os.path.exists(filePath): raise QueueError('Path not found: %s' % filePath)
    return filePath.strip()

def fillPath(rootPath, relativeFolderPath, relativeFilePath):
    folderPath = os.path.join(rootPath, relativeFolderPath)
    filePath = os.path.join(folderPath, relativeFilePath)
    return os.path.abspath(filePath)

def makeTimestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def makeFolderSafely(folderPath):
    if not os.path.exists(folderPath): os.mkdir(folderPath)
    return folderPath

def removeSafely(filePath):
    if os.path.exists(filePath): os.remove(filePath)


# Information

def saveInformation(filePath, valueByOptionBySection, fileExtension='info'):
    # Initialize
    configuration = ConfigParser.RawConfigParser()
    # For each section,
    for section in valueByOptionBySection:
        # Initialize
        valueByOption = valueByOptionBySection[section]
        # Add section
        addConfigurationSection(configuration, section, valueByOption)
    # Write
    filePath = replaceFileExtension(filePath, fileExtension)
    configuration.write(open(filePath, 'wt'))

def addConfigurationSection(configuration, section, valueByOption):
    # Add section
    configuration.add_section(section)
    # For each option,
    for option in valueByOption:
        # Initialize
        value = valueByOption[option]
        # If value is a dictionary,
        if isinstance(value, dict):
            # Add section
            addConfigurationSection(configuration, '%s.%s' % (section, option), value)
        # Otherwise
        else:
            # Add option
            configuration.set(section, option, value)

def loadInformation(filePath, fileExtension='info'):
    # Initialize
    configuration = ConfigParser.RawConfigParser()
    valueByOptionBySection = {}
    # Read
    filePath = replaceFileExtension(filePath, fileExtension)
    configuration.read(filePath, 'utf-8')
    # For each section,
    for section in configuration.sections():
        # Initialize
        valueByOption = {}
        # For each option,
        for option in configuration.options(section):
            # Get option and value
            valueByOption[option] = configuration.get(section, option)
        # Store
        valueByOptionBySection[section] = valueByOption
    # Return
    return valueByOptionBySection

def loadQueue(queuePath, convertByName):
    # Load
    valueByNameBySection = loadInformation(queuePath, fileExtension='queue')
    sections = valueByNameBySection.keys()
    # Convert values
    for section in sections:
        valueByNameBySection[section] = convertValueByName(valueByNameBySection[section], convertByName)
    # Set globalParameterByName
    globalParameterByName = valueByNameBySection.get('parameters', {})
    if 'parameters' in sections: 
        sections.remove('parameters')
    # Set parameterByTaskByName
    parameterByTaskByName = {}
    for section in sections:
        # Load
        valueByName = globalParameterByName.copy()
        valueByName.update(valueByNameBySection[section])
        # Save
        parameterByTaskByName[section] = valueByName
    # Return
    return parameterByTaskByName

def convertValueByName(valueByName, convertByName):
    # For each name,
    for name, value in valueByName.items():
        # Convert
        try: 
            convert = convertByName[name]
            valueByName[name] = convert(value)
        except KeyError:
            raise QueueError('%s is undefined' % name)
        except ValueError: 
            raise QueueError('%s=%s has the wrong type' % (name, value))
    # Return
    return valueByName

def stringifyList(items):
    return '\n' + '\n'.join(str(x) for x in items)

def stringifyNestedList(lists):
    return '\n' + '\n'.join(' '.join(str(item) for item in list) for list in lists)

def unstringifyStringList(content):
    lines = map(str.strip, content.splitlines())
    return filter(lambda line: True if line else False, lines)

def unstringifyFloatList(content):
    return map(float, content.split())

def unstringifyIntegerList(content):
    return map(int, content.split())

def unstringifyNestedIntegerList(content):
    return [[int(x) for x in line.split()] for line in unstringifyStringList(content)]

class Information(object):

    def __init__(self, informationPath):
        self.informationPath = informationPath
        self.information = loadInformation(informationPath)
        self.parameterByName = self.information.get('parameters', {})
        self.experimentPath = os.path.dirname(os.path.dirname(os.path.dirname(informationPath)))

    def expandPath(self, relativePath):
        return os.path.join(self.experimentPath, relativePath)


# Time

def recordElapsedTime(function):
    # Define wrapper
    def wrapper(*args, **kwargs):
        # Run
        startTimeInSeconds = time.time()
        resultByName = function(*args, **kwargs)
        endTimeInSeconds = time.time()
        # Record
        elapsedTimeInSeconds = int(round(endTimeInSeconds - startTimeInSeconds))
        if not resultByName: 
            resultByName = {}
        resultByName['elapsed time in seconds'] = elapsedTimeInSeconds
        print 'elapsed time in seconds = %s' % elapsedTimeInSeconds
        # Return
        return resultByName
    # Return
    return wrapper


# Module

def getLibraryModule(moduleName):
    return __import__('libraries.' + moduleName, fromlist=['libraries'])


# Error

class QueueError(Exception):
    pass
