#!/usr/bin/env python

# system modules
import sys, threading, time, os

# my modules
import FileHandler, Updater

## This module handles standard output to the user.
#
# @file Output.py
# @version 1.2

##The class which holds the information regarding print colors to the console.
class Colors:    
    ## Initialize the colors class.
    #
    # @param optionsList The settings list for how the search will be performed.
    def __init__(self, optionsList):
        ## Blue(ish) console color in ANSI.
        self.BLUE = ''
        ## Green(ish) console color in ANSI.
        self.GREEN = ''
        ## Cyan(ish) console color in ANSI.
        self.CYAN = ''
        ## Alert console color in ANSI.
        self.ALERT = ''
        ## Error console color in ANSI.
        self.ERROR = ''
        ## End console color in ANSI.
        self.END = ''
        
        self.setColors(optionsList)
    
    ## Called when the optionsList preferences have been changed to set the colors.
    #
    # @param self A pointer to the local class.
    # @param optionsList The settings list for how the search will be performed.
    def setColors(self, optionsList):
        if optionsList[11]:
            self.BLUE = '\033[94m'
            self.GREEN = '\033[32m'
            self.CYAN = '\033[36m'
            self.ALERT = '\033[33m'
            self.ERROR = '\033[31m'
            self.END = '\033[0m'
        else:
            self.BLUE = ''
            self.GREEN = ''
            self.CYAN = ''
            self.ALERT = ''
            self.ERROR = ''
            self.END = ''
    
    ## Returns the blue color ANSI code.
    #
    # @param self A pointer to the loca class.
    def blue(self):
        return self.BLUE
     
    ## Returns the green color ANSI code.
    #
    # @param self A pointer to the loca class.
    def green(self):
        return self.GREEN
    
    ## Returns the cyan color ANSI code.
    #
    # @param self A pointer to the loca class.
    def cyan(self):
        return self.CYAN
    
    ## Returns the alert color ANSI code.
    #
    # @param self A pointer to the loca class.
    def alert(self):
        return self.ALERT
    
    ## Returns the error color ANSI code.
    #
    # @param self A pointer to the loca class.
    def error(self):
        return self.ERROR
    
    ## Returns the end color ANSI code.
    #
    # @param self A pointer to the loca class.
    def end(self):
        return self.END

## Returns the current number of results found.
#
# @param results The list of folder results, file results, and in file results.
# @return The number of results.
def getNumResults(results):
    # get the number of results
    numResults = 0
    if len(results[0]) > 0:
        numResults += len(results[0])
    if len(results[1]) > 0:
        numResults += len(results[1])
    if len(results[2]) > 0:
        numResults += len(results[2])
    
    return numResults

## Clear whatever console the application is running in.
def clearScreen():
    if os.name == 'posix':
        os.system('echo -e \033c')
    elif os.name == 'nt':
        os.system('cls')
    else:
        # any other operating system commands?
        os.system('cls')

## An independent thread that is responsible for displaying the current status of the ongoing search.
class Status(threading.Thread):
    ## Initialize the local class variables with passed in variables.
    #
    # @param self A pointer to the local class.
    # @param optionsList The settings list for how the search will be performed.
    # @param string The string being searched for.
    # @param search A pointer to the thread that does the search walk.
    # @param done True if the search is done, False otherwise.
    # @param colors The colors class for output.
    def __init__(self, optionsList, string, search, done, colors):
        threading.Thread.__init__(self)
        
        ## The top-level directory being searched.
        self.path = optionsList[5]
        ## True if a Deep Search is enabled, False otherwise.
        self.deepSearch = optionsList[0]
        ## The string being searched for.
        self.string = string
        ## A pointer to the threat that does the search walk.
        self.search = search
        ## True if the search is done, False otherwise.
        self.done = done
        ## The pointer to the remote FTP connection, if established
        self.ftpLocation = optionsList[6]
        ## If the screen is to be cleared when the search starts and before results are displayed.
        self.toClearScreen = optionsList[7]
        ## The colors class for output.
        self.colors = colors
    
    ## A peek at the current state of the status thread.
    #
    # @param self A pointer to the local class.
    def peek(self):
        pass
        
    ## Executed when the thread is finished.
    #
    # @param self A pointer to the local class.
    def finish(self):
        self.done = True
        
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
    
    ## Sleeps for a given number of hundredths of a second.
    #
    # @param self A pointer to the local class.
    # @param count How many counts to wait.
    def sleep(self, count):
        for i in range(0, count):
            time.sleep(0.01)
            if self.done:
                return
    
    ## The method executed when the thread starts running. Loops through a 'Searching' animation and displays real-time search count results.
    #
    # @param self A pointer to the local class.
    def run(self):
        if self.toClearScreen:
            clearScreen()
        # if animation shouldn't be displayed, return
        if self.search.optionsList[10] == 0:
            sys.stdout.write(self.colors.green() + '\nSearching with animations disabled ...' + self.colors.end())
            sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')
            sys.stdout.flush()
            return
        
        print(self.colors.green() + 'In ' + self.path + ' and all its subfolders, FastSearch is %s' % (self.deepSearch and 'performing a Deep Search ' \
              or 'searching ') + 'for the string \'' + self.string + '\'.' + self.colors.end())
          
        # wait for the search to finish and show a progress to reassure the user
        sys.stdout.write(self.colors.green() + '\nSearching -' + self.colors.end())
        sys.stdout.flush()
        
        line = ''
        dirLine = ''
        # output results loop until finished
        while not self.done:
            spin = ['\\', '|', '/', '-']
            for i in range(0, len(spin)):
                self.sleep(10)
                sys.stdout.write('\b' + spin[i])
                sys.stdout.flush()
            
                if self.done:
                    break
            
            # output result count, if any found
            numResults = getNumResults(self.search.peek())
            if numResults > 0:
                line = '               Found ' + str(numResults) + ' Result%s' % (numResults != 1 and 's' or '')
                sys.stdout.write(self.colors.green() + line + self.colors.end())
                sys.stdout.flush()
			
			# print two levels in current directory being searched
            if self.search.optionsList[10] == 2:
                if self.ftpLocation == None:
                    curDir = self.relPath(self.search.curDir, self.path)
                else:
                    curDir = self.search.curDir
                
                if not self.ftpLocation == None:
                    curDir = curDir + os.sep
                elif len(curDir) > 20:
                    curDir = '[root]' + os.sep + curDir[:curDir.find(os.sep, 20) + 1] + '...'
                else:
                    curDir = '[root]' + os.sep + curDir + os.sep
                
                for char in dirLine:
                    sys.stdout.write(' ')
                for char in dirLine:
                    sys.stdout.write('\b')
                
                dirLine = '          Searching in: ' + curDir
                sys.stdout.write(self.colors.green() + dirLine + self.colors.end())
                
                for char in dirLine:
                    sys.stdout.write('\b')
                sys.stdout.flush()
            
            for char in line:
                sys.stdout.write('\b')
		
		# wipe search count from line, if it was displayed
        if not line == None:
            for char in line, dirLine:
                sys.stdout.write(' ')
            for char in line, dirLine:
                sys.stdout.write('\b')
		
        sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b           \b\b\b\b\b\b\b\b\b\b\b')
        sys.stdout.flush()
		
        if self.toClearScreen:		
            clearScreen()

## This method displays the current options to the user.
#
# @param optionsList The settings list for how the search will be performed.
# @param colors The colors class for output.
def options(optionsList, colors):
    print(colors.cyan() + '\n-----FASTSEARCH--OPTIONS--------------')
    print('--DEFAULT OPTIONS--')
    print('Specify which options you would like to be used as your')
    print('default options for searches. When you are finished,')
    print('type \'go (b)ack\'.')
    print('::Current States::')
    print('    (D)eep Search: %s' % (optionsList[0] and 'Yes' or 'No'))
    print('        Searches the contents of each file that is readable')
    print('        by FastSearch.')
    print('        NOTE: If run at a high level, a Deep Search may take an')
    print('        extremely long time to run completely!')
    print('    F(i)les, Fold(e)rs, or B(o)th: %s' % (optionsList[1] == 0 and 'Files Only' or optionsList[1] == 1 \
	    					         and 'Folders Only' or 'Both'))
    print('        Specify the types of results displayed for your search.')
    print('    Show (H)idden Files and Folders: %s' % (optionsList[2] and 'Yes' or 'No'))
    print('        Choose whether to include or ignore hidden files and folders.')
    print('    (F)ull Path, (R)elative Path, or (N)o Path: %s' % (optionsList[3] == 0 and 'Full Path' \
							          or optionsList[3] == 1 and 'Relative Path' \
							          or optionsList[3] == 2 and 'No Path'))
    print('        Choose to display results with full (absolute), relative,')
    print('        or no path.')
    print('        NOTE: A full (absolute) path is always shown in the results')
    print('        of remote searches.')
    print('     F(u)ll Search: %s' % (optionsList[4] and 'Yes' or 'No'))
    print('        If a full search is disabled, FastSearch will stop at the first')
    print('        result.')
    print('     (S)ave Recent Searches: %s' % (optionsList[8] and 'Yes' or 'No'))
    print('        Store information regarding recent searches (including their')
    print('        results) in RecentSearches.txt.')
    print('     (C)lear Screen: %s' % (optionsList[7] and 'Yes' or 'No'))
    print('        Choose to clean the screen up before a search is started and')
    print('        before the search results are displayed.')
    #print '     (T)hreads Used: ' + str(optionsList[9])
    #print '        Increasing the number of threads used may increase search'
    #print '        speeds. However, this may be very unsafe. Change at your own'
    #print '        risk.'
    print('     (A)ll Animations, (P)inwheel Animation, or No Animation: %s' % (optionsList[10] == 0 and 'No Animations' \
                                    or optionsList[10] == 1 and 'Pinwheel Only' \
                                    or optionsList[10] == 2 and 'All Animations'))
    print('        The search animation thread displays the pin wheel and/or the')
    print('        directory currently being searched. Disabling may improve')
    print('        search speeds, but only by a few seconds. (To change, specify')
    print('        whether you want to show all animations, show pinwheel only, or')
    print('        show no animations.)')
    print('     Te(x)t Coloring: %s' % (optionsList[11] and 'Yes' or 'No'))
    print('        Choose to display to text of FastSearch in color or not. If')
    print('        you are experiencing issues with random characters being')
    print('        displayed at the beginning of each new line (\033, [94m, etc.),')
    print('        disabling this may help.')
    print('\n--ROOT DIRECTORY--')
    print('The root directory for FastSearch always defaults to the directory')
    print('from which FastSearch was executed. The root directory does not have')
    print('to be a local directory; it could also be a network drive or a remote')
    print('server, such as an FTP connection. To change the root directory,')
    print('type \'(dir)ectory\'.')
    print('The current root directory is: ' + optionsList[5])
    print('--------------------------\n' + colors.end())

## This method displays the help menu to the user.
#
# @param colors The colors class for output.
def help(colors):
    print(colors.blue() + '\n-----FASTSEARCH--HELP-----------------')
    print('--FASTSEARCH ARGUMENTS--')
    print('When executing FastSearch, you can specify certain command-line')
    print('arguments to make the program behave differently immedietly after')
    print('opening.')
    print('::QuickSearch::')
    print('    If you enter any standard string as a command-line argument for')
    print('    FastSearch, it will be used as the search string and a QuickSearch')
    print('    will immedietly be executed on the current directory. If your')
    print('    command-line arguments have special characters, you will need to')
    print('    wrap them in quotation marks.')
    print('    EXAMPLE: python FastSearch.py "alex\'s search string"')
    print('::Dashes::')
    print('    You can launch FastSearch straight into help, credits, options,')
    print('    updates, or return by specifying one of these as the command-line')
    print('    argument following a dash.')
    print('    EXAMPLE: python FastSearch.py -updates')
    print('    The return argument is a special case in which FastSeach will')
    print('    execute, run the search on the current working directory, and return')
    print('    the results back to the caller.')
    print('    EXAMPLE: python FastSearch.py -return my search string')
    print('    If you would like to run FastSearch with the return argument and')
    print('    would also like FastSearch to perform a Deep Search, you can')
    print('    acheive this by appending the deep search argument.')
    print('    EXAMPLE: python FastSearch.py -return -deepsearch "my string"')
    print('\n--THE ROOT SEARCH DIRECTORY--')
    print('FastSearch has the ability to search either local directory or')
    print('remote directories, including FTP sites. In the options menu,')
    print('type \'directory\'. You will be prompted to enter a new root')
    print('directory. Enter a valid local or remote directory.')
    print('When specifying a remote directory, you will need an active network')
    print('or internet connection. You may also be prompted for a valid username')
    print('or password to prove you have permission to access the requested server.')
    print('EXAMPLE: C:\\MyFolder\\')
    print('EXAMPLE: \\\\MyServer\\MyFolder\\')
    print('EXAMPLE: /MyUnixFolder/')
    print('EXAMPLE: ftp.mysite.com')
    print('\n--CONTACT--')
    print('If you encounter continual problems, please ensure you have the')
    print('latest version of FastSearch. If you have updated and the problems')
    print('persist, please check fastsearch.alexlaird.net for suggestions to')
    print('resolve the problem. If all else fails, please contact the')
    print('developer from the aforementioned website.')
    print('--------------------------\n' + colors.end())

## This method displays the program credits to the user.
#
# @param colors The colors class for output.
def credits(colors):
    print(colors.blue() + '\n-----FASTSEARCH--CREDITS--------------')
    print('Created by: Alex Laird')
    print('Version: ' + str(Updater.CURRENT_VERSION))
    print('FastSearch Birth:: 6/9/09')
    print('Last Updated: 9/19/09')
    print('FastSearch is designed to be a speedy, feature-rich alternative for local')
    print('and remote directory searching of both filenames and file contents.')
    print('FastSearch is dedicated to my older brother, Andrew, who has countless times')
    print('shown me the meaning of hard work and inspired me not just sit back and')
    print('live without a solution to a problem or annoynace, but to put forth a great')
    print('effort and make a solution myself.')
    print('--------------------------\n' + colors.end())

## Display the search results and the amount of time the entire traversal took.
#
# @param path The path of FastSearch.
# @param string The search string.
# @param optionsList The settings list for how the search will be performed.
# @param results The list of results to be displayed.
# @param time The time the complete search took.
# @param colors The colors class for output.
def results(path, string, optionsList, results, time, colors):
    numResults = getNumResults(results)
    
    # display how many items were found in how many seconds (rounded to two decimals) a ternary operation is emulated
    # for the potential pluralization of 'Result(s)'
    print(colors.green() + '--FastSearch Found \'' + string + '\' ' + str(numResults) + ' Time%s in ' % (numResults != 1 and 's' or '') \
          + optionsList[5] + ' in ' + str(round(time, 2)) + ' Seconds--' + colors.end())
    
    # a full search was performed
    if optionsList[4]:
        itemNum = 1
        
        # scan through and print the full path for each folder result (if folders are displayed)
        if optionsList[1] == 1 or optionsList[1] == 2:
            print(colors.green() + '\n::Matching Folder Names::' + colors.end())
            if len(results[0]) != 0:
                for item in results[0]:
                    print(colors.green() + '[' + str(itemNum) + ']: ' + item + colors.end())
                    itemNum += 1
            else:
                print(colors.alert() + '-None Found-' + colors.end())

        # scan through and print full paths for each file result (if files are displayed)
        if optionsList[1] == 0 or optionsList[1] == 2:
            print(colors.green() + '\n::Matching File Names::' + colors.end())
            if len(results[1]) != 0:
                for item in results[1]:
                    print(colors.green() + '[' + str(itemNum) + ']: ' + item + colors.end())
                    itemNum += 1
            else:
                print(colors.alert() + '-None Found-' + colors.end())

        # scan through and print full paths for each file the string was found within (if a deep search was run)
        if optionsList[0]:
            print(colors.green() + '\n::Found in Files::' + colors.end())
            if len(results[2]) != 0:
                for item in results[2]:
                    print(colors.green() + '[' + str(itemNum) + ']: ' + item[0] + '\n  On Line%s: ' % (len(item[1]) != 1 and 's' or '') + str(item[1]) + colors.end())
                    itemNum += 1
            else:
                print(colors.alert() + '-None Found-' + colors.end())
    # a partial search was performed
    else:
        # print the only folder found
        if optionsList[1] == 1 or optionsList[1] == 2:
            print(colors.green() + '\n::Matching Folder::' + colors.end())
            if len(results[0]) != 0:
                print(colors.green() + '[1]: ' + results[0][0] + colors.end())
            else:
                print(colors.alert() + '-None Found-' + colors.end())
        
        # print the only file found
        if optionsList[1] == 0 or optionsList[1] == 2:
            print(colors.green() + '\n::Matching File::' + colors.end())
            if len(results[1]) != 0:
                    print(colors.green() + '[1]: ' + results[1][0] + colors.end())
            else:
                print(colors.alert() + '-None Found-' + colors.end())

        # print the only file the string was found within
        if optionsList[0]:
            print(colors.green() + '\n::Found in File::' + colors.end())
            if len(results[2]) != 0:
                print(colors.green() + '[1]: ' + results[2][0][0] + '\n  On Line%s: ' % (len(results[2][0][1]) != 1 and 's' or '') + str(results[2][0][1]) + colors.end())
            else:
                print(colors.alert() + '-None Found-' + colors.end())
    
    # if the user desires, write this to the recent searches list
    if optionsList[8]:
        FileHandler.writeSearchHistory(path, string, optionsList, results, time)

    if os.name == 'posix':
        print(colors.alert() + '\n--To open a search result, type its corresponding number from the main menu--\n' + colors.end())
