#!/usr/bin/env python

#my modules
import Output

# system modules
import os, sys, urllib.request, urllib.parse, urllib.error

## This module handles update checks and downloads for FastSearch.
#
# @file Updater.py
# @version 1.2

## The current local version number.
CURRENT_VERSION = 1.2
PYTHON_VERSION = sys.version_info[0]

## Checks to see if there is an update available for FastSearch.
#
# @param colors The colors class for output.
# @param response True if the method should display responses to the console, False otherwise.
# @return True if an update is available, False otherwise.
def check(colors, response):
    try:
        # open a connection the current version on the server
        verUrl = urllib.request.urlopen('http://www.alexlaird.net/projects/ontheside/programs/files/fsupdates/fsver.ldf')
        version = str(verUrl.readline())
        oldestAcceptableVersion = str(verUrl.readline())
        preUpdateMessage = str(verUrl.readline())
        postUpdateMessage = str(verUrl.readline())
        
        try:
            # split the update versions
            version = version.split('=')[1].rstrip('\r\n')
            temp = ''
            index = 0
            while index < len(version) and (version[index].isdigit() or version[index] == '.'):
                temp += version[index]
                index += 1
            version = temp
            
            oldestAcceptableVersion = oldestAcceptableVersion.split('=')[1].rstrip('\r\n')
            temp = ''
            index = 0
            while index < len(version) and (oldestAcceptableVersion[index].isdigit() or oldestAcceptableVersion[index] == '.'):
                temp += oldestAcceptableVersion[index]
                index += 1
            oldestAcceptableVersion = temp
            
            # split the pre update message
            preUpdateMessage = preUpdateMessage.split('=')[1].rstrip('\r\n')
            
            # split the post update message
            postUpdateMessage = postUpdateMessage.split('=')[1].rstrip('\r\n')
            
            # check the current version with the server version
            if float(version) > CURRENT_VERSION:
                # check to ensure that our current version is not less than the oldest acceptable version
                if not oldestAcceptableVersion == '' and CURRENT_VERSION < float(oldestAcceptableVersion):
                    return [-1]
                
                return [True, preUpdateMessage, postUpdateMessage]
            else:
                return [False]
        except:
            if response:
                print(colors.error() + 'There was an inconsistency in the version file on the server. \nTry downloading the program ' \
                    'again from fastsearch.alexlaird.net or contacting the developer.\n' + colors.end())
            return None
    except:
        if response:
            print(colors.error() + 'FastSearch could not connect to the server. Check your internet connection and try again.\n' + colors.end())
        return None
    
## Downloads the latest update from the server to the local computer.
#
# @param fastSearchDir The location of FastSearch.py on the local computer.
# @param colors The colors class for output.
# @param preUpdateMessage The message to be displayed before the update is downloaded.
# @param postUpdateMessage The message to be displayed after the update is downloaded and installed successfully.
# @return True of the update was successfully installed, False if there was some unknown error.
def getUpdate(fastSearchDir, colors, preUpdateMessage, postUpdateMessage):
    try:
        # display the pre update message retreived from the server
        if not (preUpdateMessage in ('None', '', None)):
            print(colors.alert() + preUpdateMessage + colors.end())
        
        # attain a list of updates available
        sys.stdout.write(colors.alert() + 'Download updates ...' + colors.end())
        sys.stdout.flush()
        updateUrl = urllib.request.urlopen('http://www.alexlaird.net/projects/ontheside/programs/files/fsupdates/updates' + str(PYTHON_VERSION) + '.ldf')
        filesToGet = []
        filesToDelete = []
        filesToMove = []
        foldersToGet = []
        foldersToDelete = []
        
        # get the update list
        for line in updateUrl:
            # skip over comments
            if line.startswith('#') or line.startswith('//'):
                continue
            
            line = line.rstrip('\r\n').split(' ')
            if line[0] == 'getfile':
                filesToGet.append(line[1:])
            elif line[0] == 'delfile':
                filesToDelete.append(line[1])
            elif line[0] == 'movfile':
                filesToMove.append(line[1:])
            elif line[0] == 'getfolder':
                foldersToGet.append(line[1])
            elif line[0] == 'delfolder':
                foldersToDelete.append(line[1])

        # create/update folders
        for newFolder in foldersToGet:
            if not os.path.exists(fastSearchDir + newFolder):
                os.mkdir(fastSearchDir + newFolder)
        # create/update files
        for newFile in filesToGet:
            serverFile = urllib.request.urlopen('http://www.alexlaird.net/projects/ontheside/programs/files/fsupdates/' + newFile[0]).read()
            localFile = open(fastSearchDir + newFile[1], 'wb')
            localFile.write(serverFile)
            localFile.close()
        # move files
        for movFile in filesToMove:
            if os.path.exists(fastSearchDir + movFile[0]):
                oldFile = open(fastSearchDir + movFile[0], 'r')
                newFile = open(fastSearchDir + movFile[1], 'wb')
                newFile.write(oldFile.read())
                newFile.close()
        # delete files
        for delFile in filesToDelete:
            if os.path.exists(fastSearchDir + delFile):
                os.remove(fastSearchDir + delFile)
        # delete folders
        for delFolder in foldersToDelete:
            if os.path.exists(fastSearchDir + delFolder):
                os.rmdir(fastSearchDir + delFolder)
            
        print(colors.alert() + '\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\bUpdated successfully! Restarting ...' + colors.end())
        
        try:
            # replace the current process with the restarted process
            os.execlp('python', 'python', fastSearchDir + 'FastSearch.py', '-updatesuccess', postUpdateMessage)
        except:
            # couldn't be automatically restarted
            print(colors.alert() + '\nFastSearch was successfully updated but could not be automatically restarted.\nYou will need to ' \
                'restart FastSearch manually for the changes to take effect.' + colors.end())
    except:
        return False
        