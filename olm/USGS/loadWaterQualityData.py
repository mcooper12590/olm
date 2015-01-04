## Functions to load water quality data that has been processed and
## pickled by WQXtoPHREEQC

import os
import cPickle as pickle

from siteListExtraction import *
from glob import glob

DEFAULT_DIR = './Processed-Sites'

# siteListText - list of sites separated by semi-colons
# siteFile - text file with list of sites
# regEx - a wildcard expression to use in directory
def loadSiteListData(siteListText = None,
                     siteFile = None, 
                     regEx = 'USGS-*', 
                     processedSitesDir = DEFAULT_DIR,
                     loadPhreeqc = False
                     ):
    siteList = -1
    #If the needed data is provided to find the site list then use it
    if not(siteListText == None):
        #check whether we have a valid site directory
        processedSitesDir = checkSitesDir(processedSitesDir)
        siteList = siteListFromLine(siteListText, processedSitesDir = processedSitesDir)
    elif not(siteFile == None):
        #check whether we have a valid site directory
        processedSitesDir = checkSitesDir(processedSitesDir)
        siteList = siteListFromFile(siteFile, processedSitesDir = processedSitesDir)
    elif not(regEx == None):
        #check whether we have a valid site directory
        processedSitesDir = checkSitesDir(processedSitesDir)
        siteList = siteListFromRegEx(regEx, processedSitesDir = processedSitesDir)
    else:
        # if not provided then query user for needed data
        processedSitesInput = raw_input("Path of the processed sites directory (Default = ./Processed-Sites): ")
        if (processedSitesInput != ''):
            processedSitesDir = processedSitesInput
        print(processedSitesDir)
        processedSitesDir = checkSitesDir(processedSitesDir)
        modeOK = False
        while not(modeOK):
            mode = raw_input("Do you want to: \n \t 1) enter a semi-colon separated list of sites \n \t 2) provide a text file of sites \n \t \n\t 3) provide an XML list of sites \n \t 4) provide a wildcard expression to obtain sites from directory list\n Enter 1, 2, 3, or 4: ")
            if mode.isdigit():
                if ( (int(mode) > 0) and (int(mode) < 5) ):
                    modeOK = True
                else:
                    print("Invalid input")
            else:
                print("Invalid input")
        if (int(mode) == 1):
            siteListText = raw_input("Enter list of sites separated by semi-colons: ")
            siteList = siteListFromLine(siteListText)
        elif (int(mode) == 2):
            siteFile = raw_input("Enter path to text file containing site list: ")
            siteList = siteListFromFile(siteFile)
        elif (int(mode) == 3):
            siteFile = raw_input("Enter path to XML file containing site list: ")
            siteList = siteListFromFile(siteFile, XML=True)
        elif (int(mode) == 4):
            regEx = raw_input("Enter regular expression: ")
            siteList = siteListFromRegEx(regEx)
    if (siteList != -1):
        #process the sites in the list
        
        sitesDict = {}
        sitesPhreeqcDict = {}
        for site in siteList:            
            sitePanel = loadSiteData(site, processedSitesDir = processedSitesDir)
            sitesDict[site] = sitePanel
            if loadPhreeqc:
                sitedf = loadSitePhreeqcData(site, processedSitesDir = processedSitesDir)
                sitesPhreeqcDict[site] = sitedf
        if loadPhreeqc:
            return (sitesDict, sitesPhreeqcDict)
        else:
            return sitesDict



def loadSiteData(site, processedSitesDir = DEFAULT_DIR):
    #Add USGS tag if needed
    if not(site.startswith('USGS-')):
        site = 'USGS-'+site
    try:
        panelFile = os.path.join(processedSitesDir, site, site+'-Panel.pkl')
        sitePanel = pickle.load(open(panelFile, 'rb'))
    except IOError:
        print ("Problem reading pickle file: " + panelFile )
        return None
    return sitePanel

def loadSitePhreeqcData(site, processedSitesDir = DEFAULT_DIR):
    #Add USGS tag if needed
    if not(site.startswith('USGS-')):
        site = 'USGS-'+site
    try:
        phreeqcFile = os.path.join(processedSitesDir, site, site+'-PHREEQC.pkl')
        sitedf = pickle.load(open(phreeqcFile, 'rb'))
    except IOError:
        print ("Problem reading pickle file: " + phreeqcFile )
        return None
    return sitedf
            
def siteListFromLine(siteListText):
    siteList = siteListText.split(';')
    siteList = [x.strip() for x in siteList]
    #check for USGS Tag at beginning of site number
    for i, site in enumerate(siteList):
        if not(site.startswith('USGS-')):
            siteList[i] = 'USGS-' + siteList[i]
    return siteList

def siteListFromFile(siteFile, 
                     sitesDir = DEFAULT_DIR,
                     XML=False):
    if (siteFile.endswith('.xml') or (XML == True)):
        siteList = extractSitesFromXML(siteFile)
    else:
        siteList = extractSitesFromText(siteFile)
    #check for USGS Tag at beginning of site number
    for i, site in enumerate(siteList):
        if not(site.startswith('USGS-')):
            siteList[i] = 'USGS-' + siteList[i]
 #   siteList = [os.path.join(processedSitesDir, x) for x in siteList]
    return siteList

def siteListFromRegEx(regEx,
                      processedSitesDir = DEFAULT_DIR):
#    print("processedSitesDir="+processedSitesDir)
    listText = os.path.join(processedSitesDir, regEx)
    sitePath = glob(listText)
    siteList = []
    for site in sitePath:
        siteSplit = site.split('/')
        siteList.append(siteSplit[-1])
    return siteList

def checkSitesDir(processedSitesDir):
    while not os.path.exists(processedSitesDir):
        print("Invalid path to processed sites directory.")
        processedSitesDir = raw_input("Path of the processed sites directory (Default = ./Processed-Sites): ")
    return processedSitesDir
