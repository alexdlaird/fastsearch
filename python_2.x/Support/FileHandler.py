#!/usr/bin/env python

# system modules
import os
from time import strftime

# my modules
import Output

## This module contains the methods that handle the interactions in file I/O to the search.
#
# @file FileHandler.py
# @version 1.2

showColors = False

if os.name == 'posix':
    showColors = True
#elif os.name == 
    # any other environment
    #showColors = True

## The default options list to be used if none is set.
defaultList = [False, 2, True, 0, True, os.getcwd(), None, True, True, 2, 2, showColors]
## The options file name.
optionsFileName = 'Options.ldf'
## The recent searches file name.
recentSearchesFileName = 'RecentSearches.txt'

## Read the current options file (if it exists), and ensure that all its values are valid. Return the options list.
#
# @param fastSearchDir The path of FastSearch.
# @param optionsList The list of options to be stored and written.
# @return The settings list for how the search will be performed.
def initializeOptionsList(fastSearchDir, optionsList):
    # ensure that the options list file exists and initialize the array with its values
    if os.path.exists(fastSearchDir + 'Support' + os.sep + optionsFileName):
        exists = True
        try:
            optionsFile = open(fastSearchDir + 'Support' + os.sep + optionsFileName, 'r')
            
            # deep search
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[0] == 'True':
                optionsList[0] = True
            else:
                optionsList[0] = False
            # show files, folders, both
            optionsList.append(optionsFile.readline().split('#')[0])
            try:
                optionsList[1] = int(optionsList[1])
                if optionsList[1] < 0 or optionsList[1] > 2:
                    optionsList[1] = 2
            except:
                optionsList[1] = 2
            # show hidden
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[2] == 'True':
                optionsList[2] = True
            else:
                optionsList[2] = False
            # show path
            optionsList.append(optionsFile.readline().split('#')[0])
            try:
                optionsList[3] = int(optionsList[3])
                if optionsList[3] < 0 or optionsList[3] > 2:
                    optionsList[3] = 0
            except:
                optionsList[3] = 0
            # full search
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[4] == 'True':
                optionsList[4] = True
            else:
                optionsList[4] = False
            # root directory
            optionsFile.readline() # throw away one read
            optionsList.append(os.getcwd())
            # ftp pointer (for a remote location)
            optionsList.append(None)
            # clear screen before search results
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[7] == 'True':
                optionsList[7] = True
            else:
                optionsList[7] = False
            # write recent searches to file
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[8] == 'True':
                optionsList[8] = True
            else:
                optionsList[8] = False
            # number of threads used
            optionsList.append(optionsFile.readline().split('#')[0])
            try:
                optionsList[9] = int(optionsList[9])
            except:
                optionsList[9] = 2
            # display search animations
            optionsList.append(optionsFile.readline().split('#')[0])
            try:
                optionsList[10] = int(optionsList[10])
                if optionsList[10] < 0 or optionsList[10] > 2:
                    optionsList[10] = 2
            except:
                optionsList[10] = 2
            # text coloring
            optionsList.append(optionsFile.readline().split('#')[0])
            if optionsList[11] == 'True':
                optionsList[11] = True
            else:
                optionsList[11] = False
                
            
            optionsFile.close()
        except:
            # some error occured in reading the file, write a new one
            optionsList = defaultList
    # if the options file doesn't exist, make our own values
    else:
        exists = False
        optionsList = defaultList
    
    # write values to the options file
    writeNewOptionsList(fastSearchDir, optionsList, exists)
    
    return optionsList
    
## Write the options list to the options file.
#
# @param fastSearchDir The path of FastSearch.
# @param optionsList The list of options to be written.
# @param exists True if the current file exists and should be removed, False otherwise.
def writeNewOptionsList(fastSearchDir, optionsList, exists):
    if exists:
        os.remove(fastSearchDir + 'Support' + os.sep + optionsFileName)
    
    optionsFile = open(fastSearchDir + 'Support' + os.sep + optionsFileName, 'w')
    optionsFile.write(str(optionsList[0]) + '# Deep Search\n')
    optionsFile.write(str(optionsList[1]) + '# Show Files (0), Folders (1), or Both (2)\n')
    optionsFile.write(str(optionsList[2]) + '# Show Hidden Files and Folders\n')
    optionsFile.write(str(optionsList[3]) + '# Show Full (0), Relative (1), or No Path (2)\n')
    optionsFile.write(str(optionsList[4]) + '# Full Search\n')
    optionsFile.write(str(optionsList[5]) + '# Root Directory\n')
    optionsFile.write(str(optionsList[7]) + '# Clear Screen Before Displaying Search Results\n')
    optionsFile.write(str(optionsList[8]) + '# Write Recent Searches to File\n')
    optionsFile.write(str(optionsList[9]) + '# Number of Threads Used\n')
    optionsFile.write(str(optionsList[10]) + '# To display search animations\n')
    optionsFile.write(str(optionsList[11]) + '# Text coloring')
    
    optionsFile.close()
    
## Write the information regarding this search to the search history file.
#
# @param fastSearchDir The path of FastSearch.
# @param string The search string.
# @param optionsList The settings list for how the search will be performed.
# @param results The results from the search.
# @param time The amount of time the search required.
def writeSearchHistory(fastSearchDir, string, optionsList, results, time):
    # if the file already exists, append to it, otherwise create it
    if os.path.exists(fastSearchDir + 'Support' + os.sep + recentSearchesFileName):
        recentSearchesFile = open(fastSearchDir + 'Support' + os.sep + recentSearchesFileName, 'a')
    else:
        recentSearchesFile = open(fastSearchDir + 'Support' + os.sep + recentSearchesFileName, 'w')
    
    numResults = Output.getNumResults(results)
    if numResults > 0:
        recentSearchesFile.write('-----------------------------\n')
        recentSearchesFile.write('Date and Time: ' + strftime("%Y-%m-%d %H:%M:%S") + '\n')
        recentSearchesFile.write('Root Directory: ' + optionsList[5] + '\n')
        recentSearchesFile.write('Search String: ' + string + '\n')
        recentSearchesFile.write('Search Time: ' + str(time) + '\n')
        recentSearchesFile.write('Result Count: ' + str(numResults) + '\n')
        recentSearchesFile.write('\n--Results--')
        
        # scan through and print the full path for each folder result (if folders are displayed)
        if optionsList[1] == 1 or optionsList[1] == 2:
            recentSearchesFile.write('\n\n::Matching Folder Names::')
            if len(results[0]) != 0:
                for item in results[0]:
                    recentSearchesFile.write('\n' + item)
            else:
                recentSearchesFile.write('\n-None Found-')

        # scan through and print full paths for each file result (if files are displayed)
        if optionsList[1] == 0 or optionsList[1] == 2:
            recentSearchesFile.write('\n\n::Matching File Names::')
            if len(results[1]) != 0:
                for item in results[1]:
                    recentSearchesFile.write('\n' + item)
            else:
                recentSearchesFile.write('\n-None Found-')

        # scan through and print full paths for each file the string was found within (if a deep search was run)
        if optionsList[0]:
            recentSearchesFile.write('\n\n::Found in Files::')
            if len(results[2]) != 0:
                for item in results[2]:
                    recentSearchesFile.write('\n' + item[0] + '\n  On Line%s: ' % (len(item[1]) != 1 and 's' or '') + str(item[1]))
            else:
                recentSearchesFile.write('\n-None Found-')
        
        recentSearchesFile.write('\n-----------------------------\n\n')

    recentSearchesFile.close()
    
