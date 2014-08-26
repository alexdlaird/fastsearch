#!/usr/bin/env python

# system modules
import os, threading

## This module contains the specific search methods to ensure optimal performance and abstraction.
#
# @file Search.py
# @version 1.2

## An independent thread that performs the actual search.
class Search(threading.Thread):
    ## Initialize the local class variables with passed in variables.
    #
    # @param self A pointer to the local class.
    # @param string The search string to be found.
    # @param optionsList The settings list for how the search will be performed.
    def __init__(self, string, optionsList):
        threading.Thread.__init__(self)
        
        ## The search string to be found.
        self.string = string
        ## The settings list for how the search will be performed.
        self.optionsList = optionsList
        
        ## The list of folders found matching the search string.
        self.folderResults = []
        ## The list of files found matching the search string.
        self.fileResults = []
        ## The list of files containing the search string.
        self.inFileResults = []
        
        ## The current directory being searched.
        self.curDir = None
    
    ## A peek at the current state of the search thread.
    #
    # @param self A pointer to the local class.
    # @return A list of folders, files, and in files results, the search string, the options list, and the current directory.
    def peek(self):
        # return the list of results, the search string, current options list, and 
        return [self.folderResults, self.fileResults, self.inFileResults, self.string, self.optionsList, self.curDir]
    
    ## Executed when the thread is finished.
    #
    # @param self A pointer to the local class.
    # @return The list of folders, files, and in files results found.
    def finish(self):
        # return the list of results
        return [self.folderResults, self.fileResults, self.inFileResults]
    
    
    ## ***This method is derived from the Python 2.6 source of os.walk***
    #
    # Recursively walks through the ftp location for the search.
    #
    # @param self A pointer to the local class.
    # @param ftp A pointer to the ftp location (already logged in).
    # @param top The current top directory.
    # @param topDown True for a top-down search, False otherwise.
    # @return The current root, a list of dirs in the cwd, and a list of files in the cwd.
    def ftpWalk(self, ftp, top, topDown = True):
        # set the ftp directory to point at our the current top
        ftp.cwd(top)
        names = []

        # if we do not have permission to grab a certain directory, continue to the next iteration
        try:
            # retrieve a list of everything in this folder
            ftp.retrlines('LIST', names.append)
        except:
            return

        dirs, nonDirs = [], []
        for line in names:
            # split the ftp line into its sections
            words = line.split(None, 8)
            
            linkCount = words[-1].find(' -> ')
            # conditions for skipping this line element
            if len(words) < 6 or words[-1] in ('.', '..') or linkCount > 0:
                continue
            
            # store the directory or file in its respective list
            if words[0][0] == 'd':
                dirs.append(words[-1])
            else:
                nonDirs.append(words[-1])

        if topDown:
            yield top, dirs, nonDirs
        for name in dirs:
            path = os.path.join(top, name)
            # recursively enter this subdirectory
            for item in self.ftpWalk(ftp, path, topDown):
                yield item
        if not topDown:
            yield top, dirs, nonDirs
    
    ## ***This method is derived from the Python 2.6 source of os.walk***
    #
    # Recursively walks through the local location for the search.
    #
    # @param self A pointer to the local class.
    # @param top The current top directory.
    # @param topDown True for a top-down search, False otherwise.
    # @return The current root, a list of dirs in the cwd, and a list of files in the cwd.
    def localWalk(self, top, topDown = True):
        # if we do not have permission to grab a certain directory, continue to the next iteration
        try:
            # retrieve a list of everything in this folder
            names = os.listdir(top)
        except:
            return
    
        dirs, nonDirs = [], []
        for name in names:
            # store the directory or file in its respective list
            if os.path.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nonDirs.append(name)
    
        if topDown:
            yield top, dirs, nonDirs
        for name in dirs:
            path = os.path.join(top, name)
            if not os.path.islink(path):
                # recursively enter this subdirectory
                for x in self.localWalk(path, topDown):
                    yield x
        if not topDown:
            yield top, dirs, nonDirs
    
    ## ***This method is derived from the Python 2.6 source to ensure that FastSearch works with users running Python versions older than 2.6***
    #
    # Returns a relative version of the path specified.
    #
    # @param self A reference to the current class.
    # @param path The specified path.
    # @param start The directory to make relative; current directory if none is specified.
    # @return The relative version of the path.
    def relPath(self, path, start = '.'):
        startList = os.path.abspath(start).split(os.path.sep)
        pathList = os.path.abspath(path).split(os.path.sep)
    
        i = len(os.path.commonprefix([startList, pathList]))

        relList = ['..'] * (len(startList) - i) + pathList[i:]
        if not relList:
            return '.'
        return os.path.join(*relList)
    
    ## This method searches within an individual file for the desired search string.
    #
    # @param self A pointer to the local class.
    # @param path The path to the file to be search.
    # @param fileName The name of the file to be searched.
    # @return A list of line number(s) the result was found on.
    def deepSearch(self, path, fileName):
        # declare deep search local variables
        results = []
        lineNumber = 1
        fileStream = open(os.path.join(path, fileName), 'r')

        # scan through each line of the file looking for our search string
        for line in fileStream:
            # when a result is found, append it to the results list
            if line.lower().rfind(self.string) != -1:
                results.append(lineNumber)
            # increment the line number since the loop won't keep track
            lineNumber += 1

        # don't forget to close the files!
        fileStream.close()

        # return the deep search results
        return results
    
    ## Checks to see if the current item is a hidden file or folder and should be excluded.
    #
    # @param self A pointer to the local class.
    # @param string The string to check.
    # @return True if the file is a hidden file and should be excluded, False otherwise.
    def hiddenExclude(self, string):
        if string.startswith('.') or string.startswith('~') or string.endswith('~') or string.endswith('.tmp') \
           or string.endswith('.temp'):
            return True
        else:
            return False
    
    ## Checks to see if the current item is one that a Deep Search should not scan through.
    #
    # @param self A pointer to the local class.
    # @param string The string to check.
    # @return True if the file should be excluded from a Deep Search, False otherwise.
    def deepSearchExclude(self, string):
        if string.endswith('.exe') or string.endswith('.zip') or string.endswith('.tar') \
           or string.endswith('.bz') or string.endswith('.gz') or string.endswith('.hqx') or string.endswith('.app') \
           or string.endswith('.dll') or string.endswith('.mov') or string.endswith('.mpeg') or string.endswith('.mpg') \
           or string.endswith('.wmv') or string.endswith('.avi') or string.endswith('.dv') or string.endswith('.jpg') \
           or string.endswith('.jpeg') or string.endswith('.bmp') or string.endswith('.png') or string.endswith('.psd'):
            return True
        else:
            return False
    
    ## Searches this item in the walk for the specific search string by the given options within optionsList.
    #
    # @param self A pointer to the local class.
    # @param root The current directory being scanned.
    # @param dirs A list of directories within this root.
    # @param files A list of files within this root.
    # @return A Full Search returns a 0 upon successful scanning, and a Partial Search returns a -1.
    def scanItem(self, root, dirs, files):
        # if folders are to be shown
        if self.optionsList[1] == 1 or self.optionsList[1] == 2:
            # the folder name is stored in the second tuple value
            for folder in dirs[:]:
                # remove hidden folders (if requested) so the walk won't traverse down them
                if not self.optionsList[2] and self.hiddenExclude(folder):
                    dirs.remove(folder)
                    continue
                
                # check to see if the current folder name matches the search string
                if folder.lower().rfind(self.string) != -1:
                    # add it to the results list
                    if self.optionsList[3] == 0 or not self.optionsList[6] == None:
                        self.folderResults.append(os.path.join(os.path.abspath(root), folder))
                    elif self.optionsList[3] == 1:
                        self.folderResults.append(os.path.join(self.relPath(root, self.optionsList[5]), folder))
                    else:
                        self.folderResults.append(folder)
                    
                    # if this is not a full search, we're done
                    if not self.optionsList[4]:
                        return -1
                        
        # if files are to be shown
        if self.optionsList[1] == 0 or self.optionsList[1] == 2:
            # the file name is stored in the third tuple value
            for fileName in files:
                # skip over hidden files
                if (not self.optionsList[2]) and self.hiddenExclude(fileName):
                    continue
                
                # check to see if the user wants a deep search and that the file is a readable type
                if self.optionsList[0] and not self.deepSearchExclude(fileName):
                    lineNumbers = self.deepSearch(os.path.abspath(root), fileName)
                    # if the deep search found a result, append it along with the line number(s) of the match
                    if len(lineNumbers) != 0:
                        if self.optionsList[3] == 0 or not self.optionsList[6] == None:
                            self.inFileResults.append([os.path.join(os.path.abspath(root), fileName), lineNumbers])
                        elif self.optionsList[3] == 1:
                            self.inFileResults.append([os.path.join(self.relPath(root, self.optionsList[5]), fileName), lineNumbers])
                        else:
                            self.inFileResults.append([fileName, lineNumbers])
                        
                        # if this is not a full search, we're done
                        if not self.optionsList[4]:
                            return -1
                    
                # check to see if the current file name matches the search string
                if fileName.lower().rfind(self.string) != -1:
                    # add it to the results list
                    if self.optionsList[3] == 0 or not self.optionsList[6] == None:
                    	self.fileResults.append(os.path.join(os.path.abspath(root), fileName))
                    elif self.optionsList[3] == 1:
                        self.fileResults.append(os.path.join(self.relPath(root, self.optionsList[5]), fileName))
                    else:
                        self.fileResults.append(fileName)
                        
                    # if this is not a full search, we're done
                    if not self.optionsList[4]:
                        return -1
        return 0
        
    ## This method is responsible for the top-down traversal from the root directory specified.
    # A full list of search matches is stored in the results list and returned upon search completion.
    # (finish() must be called to actually return this list.)
    #
    # @param self A pointer to the local class.
    # @return The list of the results.
    def run(self):
        # the search walk starts at the specified root directory; the search is a top-down traversal
        if self.optionsList[6] == None:
            # perform a local search
            for root, dirs, files in self.localWalk(self.optionsList[5]):
                self.curDir = root
                value = self.scanItem(root, dirs, files)
                if value == -1:
                    break
        else:
            # perform a remote search
            for root, dirs, files in self.ftpWalk(self.optionsList[6], self.optionsList[6].pwd()):
                self.curDir = root
                value = self.scanItem(root, dirs, files)
                if value == -1:
                    break
            
            # reset the current working directory on the server in case the user does a second search
            if not self.optionsList[5].find('/') == -1:
                self.optionsList[6].cwd(self.optionsList[5][self.optionsList[5].find('/'):])
            else:
                self.optionsList[6].cwd('/')
                