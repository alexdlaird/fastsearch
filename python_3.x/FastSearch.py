#!/usr/bin/env python

# system modules
import os, sys, threading, time
# add subfolders to the path so imports work correctly
sys.path.append(os.path.abspath(sys.argv[0])[:os.path.abspath(sys.argv[0]).rfind(os.sep)] + os.sep + 'Support' + os.sep)

# my modules
import FileHandler, Options, Output, Search, Updater

## FastSearch is designed to be a speedy, feature-rich alternative for local and remote directory searching of both filenames and file contents.
# FastSearch is dedicated to my older brother, Andrew, who has countless times shown me the meaning of hard work and inspired me not just sit back and
# live without a solution to a problem or annoynace, but to put forth a great effort and make a solution myself.
#
# @author Alex Laird
# @date FastSearch Birth: 6/9/09
# @date Last Updated: 10/7/09
#
# @file FastSearch.py
# @version 1.2
# @bug The Output.Status thread slows the searches down by a few seconds, which is intolerable
# @todo Allow pressing of the tab key when specifying a new root directory to display a list of available folders within the current directory (not sure how to implement this one with Python).
# @todo Allow the user to press escape to terminate the search and display current results (not sure how to implement this one with Python).
# @todo The 'open' command for a search result only works in posix.  Make it work in Windows.
# @todo Split the FastSearch walk x number of times and launch a thread to cover each division; allow the user to specify what x should be. Then uncomment the Options menu code.
# @todo If it's not too much of a performance hit, launch a new thread to scan through past searches to use old results.
# @todo Add WebDAV server support.
# @todo Add support for regular expressions.

## Return code if the program executed and terminated properly.
EXIT_CLEAN = 0
## Return code if some unknown error occured in the program.
EXIT_UNKNOWN_ERROR = 1
## Return code if the program executed properly and returned results to the caller.
EXIT_RESULTS = 2
## Return code if the program executed for results but errored.
EXIT_RESULTS_BAD = 3
## Return code if a debug was run.
EXIT_DEBUG = 4
## Return code if a debug was run and some error occured.
EXIT_DEBUG_ERROR = 5

## Splits a list num times and returns a list of lists containing the original elements.
#
# @param oldList The list to be split.
# @param num The number of times to split the list.
# @return A list of num lists containing the original elements.
def splitList(oldList, num):
    newList = []
    size = (1.0 / num) * len(oldList)
    for i in range(num):
            newList.append(oldList[int(round(i * size)):int(round((i + 1) * size))])
    return newList

## Where the searching call and output calls are instantiated from.
#
# @param path The path of FastSearch.
# @param string The string to be searched for.
# @param optionsList The settings list for how the search will be performed.
# @param returnResults True if the results are to be returned, False otherwise.
# @param colors The colors class for output.
# @return The exit code and the results.
def runSearch(path, string, optionsList, returnResults, colors):
    # start the search thread and timer
    startTime = time.time()
    search = Search.Search(string, optionsList)
    search.start()
    
    # start the status thread
    status = Output.Status(optionsList, string, search, False, colors)
    status.start()
    
    # join the threads and grab the results
    search.join()
    results = search.finish()
    status.finish()
    status.join()
    
    # calculate the elapsed time
    elapsedTime = (time.time() - startTime)

    # print the search results
    Output.results(path, string, optionsList, results, elapsedTime, colors)
    
    if returnResults:
        return EXIT_RESULTS, results
    else:
        return EXIT_CLEAN, results

## Checks to see if any updates are available, prompts the user if there are, and downloads and installs them.
#
# @param fastSearchDir The location on the local computer of FastSearch.
# @param colors The colors class for output.
def runUpdater(fastSearchDir, colors):
    available = Updater.check(colors, True)
    if not available == None:
        if available[0] == True:
            response = input(colors.blue() + 'There is an update available. Download? ' + colors.end()).lower()
            if response in ('y', 'yes', 'u', 'update', 'd', 'download', 'get', 'get it', 'install', 'install update'):
                verified = Updater.getUpdate(fastSearchDir, colors, available[1], available[2])
                if not verified:
                    print(colors.error() + '\nAn error occurred while trying to download and install the update. Check your internet connection and ' \
                        'try again.\nIf the problem persists, try downloading the program again from fastsearch.alexlaird.net or contacting the developer.\n' + colors.end())
            else:
                print(colors.alert() + 'No updates were downloaded or installed.\n' + colors.end())
        elif available[0] == -1:
            print(colors.alert() + 'An update is available, but the current version of FastSearch cannot be automatically updated.\nPlease navigate to ' \
                'fastsearch.alexlaird.net in order to download and install the update.\n' + colors.end())
        else:
            print(colors.alert() + 'There are no updates available at this time.\n' + colors.end())

## The debug thread for a standard os.walk comparison.
class Debug(threading.Thread):
    ## Initialize the local Debug class with passed in variables.
    #
    # @param self A pointer to the local class.
    # @param string The search string.
    # @param optionsList The default settings for a debug search.
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
    
    ## Run the debug os.walk method in its own thread.
    #
    # @param self A pointer to the loca class.
    def run(self):
        for root, dirs, files in os.walk(self.optionsList[5]):
            for folder in dirs:
                if folder == '':
                    pass
            for fileName in files:
                if fileName == '':
                    pass

## Runs the debugging procedure for FastSearch.
#
# @param args The command-line arguments.
# @param colors The colors class for output.
# @return 4 if the debug was successful, 5 if an unknown error occured.
def debug(args, colors):
    start = 0
    try:
        stop = int(args[2])
    except:
        stop = 5
    
    differences = []
    print(colors.alert() + '---RUNNING IN DEBUG MODE---')
    for i in range(start, stop):
        print('--Running Iteration ' + str(i + 1) + ' of ' + str(stop) + '--')
        startTimeOs = time.time()
        print('::Running Standard Search Algorithm Benchmark::')
        print('Running Standard Search: ' + str(startTimeOs))
        debug = Debug('', [False, 2, True, 0, True, os.getcwd(), None, True, True, 1])
        debug.start()
        debug.join()
        endTimeOs = time.time()
        print('Standard Search complete: ' + str(endTimeOs))
        elapsedTimeOs = endTimeOs - startTimeOs
        print('Total time for Standard Search: ' + str(elapsedTimeOs))
        print('\n::Running Single-Threaded FastSearch Algorithm Benchmark::')
        startTimeFsS = time.time()
        print('Running Single-Threaded FastSearch: ' + str(startTimeFsS))
        search = Search.Search('', [False, 2, True, 0, True, os.getcwd(), None, True, True, 1])
        search.start()
        search.join()
        endTimeFsS = time.time()
        print('Single-Threaded FastSearch complete: ' + str(endTimeFsS))
        elapsedTimeFsS = endTimeFsS - startTimeFsS
        print('Total time for Single-Threaded FastSearch: ' + str(elapsedTimeFsS))
        print('\n::Running Multi-Threaded FastSearch Algorithm Benchmark::')
        startTimeFsM = time.time()
        print('Running Multi-Threaded FastSearch: ' + str(startTimeFsM))
        search = Search.Search('', [False, 2, True, 0, True, os.getcwd(), None, True, True, 2])
        search.start()
        search.join()
        endTimeFsM = time.time()
        print('Multi-Threaded FastSearch complete: ' + str(endTimeFsM))
        elapsedTimeFsM = endTimeFsM - startTimeFsM
        print('Total time for Multi-Threaded FastSearch: ' + str(elapsedTimeFsM))
        print('\n::Iteration ' + str(i + 1) + ' of ' + str(stop) + ' Complete::')
        differences.append(elapsedTimeFsS - elapsedTimeOs)
        print('Difference between Standard Search and Single-Threaded FastSearch: ' + str(differences[i]) + '\n')
        print('Difference between Single and Multi-Threaded FastSearch: ' + str(elapsedTimeFsS - elapsedTimeFsM) + '\n')
    
    total = 0
    for item in differences:
        total += item
    avg = total / len(differences)
    
    print('----------------------------')
    if avg > 0:
        print('On averge, Standard Search was ' + str(avg) + ' seconds faster than Single-Threaded FastSearch.')
    else:
        print('On averge, Single-Threaded FastSearch was ' + str(avg * (-1)) + ' seconds faster than Standard Search.')
    print('----------------------------')
    print('---EXITING DEBUG MODE---\n' + colors.end())
    
    return EXIT_DEBUG
    
## Checks for updates prior to the program run.
#
# @param colors The colors class for output.
def simpleUpdateChecker(colors):
    # run the autmoatic updater, but only alert if an update is available
    available = Updater.check(colors, False)
    if not available == None and available[0]:
        response = input(colors.alert() + '::Update Alert::\nThere is an update available. Would you like to download it now? ' + colors.end()).lower()
        if response in ('y', 'yes', 'u', 'update', 'd', 'download', 'get', 'get it', 'install', 'install update'):
            verified = Updater.getUpdate(fastSearchDir, colors, available[1], available[2])
            if not verified:
                print(colors.error() + '\nAn error occurred while trying to download and install the update. Check your internet connection and try again.\nIf the problem persists, contact the developer.\n' + colors.end())
        else:
            print(colors.alert() + 'No updates were downloaded or installed.\n' + colors.end())

## This method handles the input, output, and clean exit of the search program.
#
# @param args The command-line arguments.
def main(args):
    # get the absolute path of the FastSearch directory
    fastSearchDir = os.path.abspath(args[0])[:os.path.abspath(args[0]).rfind(os.sep)] + os.sep
    
    # instantiate the exit code
    code = EXIT_CLEAN
    
    # instantiate pre-run update condition
    preRunUpdateCheck = False
    
    # declare options list
    optionsList = FileHandler.initializeOptionsList(fastSearchDir, [])
    colors = Output.Colors(optionsList)
    
    # FastSearch has been updated
    if len(args) > 3 and args[1] == '-updatesuccess':
        print(colors.alert() + '\nFastSearch has been successfully updated to v' + str(Updater.CURRENT_VERSION) + '!' + colors.end())
        # display the post update message retrieved from the server
        if not (args[2] in ('None', '', None)):
            print(colors.alert() + args[2:] + colors.end())
    
    # run a QuickSearch and return the results as a list and quit the application
    if len(args) > 1 and args[1][1:].lower() in ('r', 'return'):
        if len(args) > 2:
            optionsList = FileHandler.defaultList
            if len(args) > 3 and args[2][1:].lower() in ('d', 'deep', 'deepsearch', 'ds'):
                optionsList[0] = True
                start = 3
            else:
                start = 2
            
            # if the user requested a deep search but provided no string
            if args[start][1:] in ('d', 'deep', 'deepsearch', 'ds'):
                return EXIT_RESULTS_BAD, None
            
            string = args[start].lower()            
            for i in range(start + 1, len(args)):
                string += ' ' + args[i].lower()
            
            search = Search.Search(string, optionsList, colors)
            search.start()
            search.join()
            return EXIT_RESULTS, search.finish()
        else:
            return EXIT_RESULTS_BAD, None
    
    print(colors.blue() + '\n::Welcome to FastSearch v' + str(Updater.CURRENT_VERSION) + ' by Alex Laird::' + colors.end())
    
    # if arguments are specified, use them as the search string
    if len(args) > 1 and not args[1] == '-updatesuccess':
        if args[1].startswith('-'):
            if len(args) == 2 and not args[1][1:].lower() in ('d', 'debug'):
                if args[1][1:].lower() in ('help', 'h'):
                    Output.help(colors)
                elif args[1][1:].lower() in ('update', 'updates', 'u'):
                    runUpdater(fastSearchDir, colors)
                elif args[1][1:].lower() in ('credit', 'credits', 'c'):
                    Output.credits(colors)
                elif args[1][1:].lower() in ('option', 'options', 'o', 'pref', 'preferences', 'setting', 'settings'):
                    optionsList = Options.options(fastSearchDir, optionsList, colors)
                else:
                    print(colors.alert() + 'The command-line arguments were not valid. View the help menu for assistance.\n' + colors.end())
            # run a benchmark comparing a standard os.walk method (with no comparisons) to the FastSearch localWalk method
            elif args[1][1:].lower() in ('d', 'debug'):
                try:
                    code = debug(args, colors)
                except:
                    code = EXIT_DEBUG_ERROR
                
                return code
            else:
                print(colors.alert() + 'The command-line arguments were not valid. View the help menu for assistance.\n' + colors.end())
        else:
            string = args[1].lower()
            for i in range(2, len(args)):
                string += ' ' + args[i].lower()
    
            # the search will be launched immedietly with the current working directory as root
            code = runSearch(fastSearchDir, string, optionsList, False, colors)[0]
    # if no arguments were specified
    elif len(args) == 1:
        if preRunUpdateCheck:
            simpleUpdateChecker(colors)

    looping = True
    results = None
        
    # loop until the user wants out
    while looping:
        # retreive a command from the user
        string = input(colors.blue() + 'Type (s)earch, (o)ptions, (u)pdate, (h)elp, (c)redits, or (q)uit: ' + colors.end()).lower()
        
        # the user entered a number
        if string.strip('[]').isdigit():
            if not results == None:
                location = int(string.strip('[]')) - 1
                ref = 0
                # decrement the number as needed to keep it consistent with the correct results subarray
                if location > len(results[0]) - 1:
                    location -= len(results[0])
                    ref = 1
                if location > len(results[1]) - 1:
                    location -= len(results[1])
                    ref = 2
                
                # ensure that the location is/was a valid search result
                if location < 0 or location > len(results[ref]) - 1:
                    print(colors.alert() + 'The number entered did not correspond to a search results. Try again.\n' + colors.end())
                
                # launch the search result
                print('Opening ' + os.path.abspath(results[ref][location]) + ' ...')
                os.system('open ' + os.path.normpath(os.path.abspath(results[ref][location])).replace(' ', '\\ '))
                print('')
            else:
                print(colors.alert() + '\nThat wasn\'t an option. Try again.\n' + colors.end())
            
            continue

        # the user wants to search
        if string in ('s', 'search', 'f', 'find'):
            # retreive the string to search for from the user
            string = input(colors.blue() + 'Enter a search string: ' + colors.end()).lower()
            
            code, results = runSearch(fastSearchDir, string, optionsList, False, colors)
        # the user wants to check for updates
        elif string in ('u', 'update', 'updates'):
            runUpdater(fastSearchDir, colors)
        # the user wants help
        elif string in ('h', 'help'):
            Output.help(colors)
        # the user wants to see the credits
        elif string in ('c', 'credit', 'credits'):
            Output.credits(colors)
        # the user wants to specify search options
        elif string in ('o', 'options', 'p', 'pref', 'prefs', 'preferences', 'setting', 'settings'):
            optionsList = Options.options(fastSearchDir, optionsList, colors)
        # the user wants to end the program
        elif string in ('q', 'quit', 'e', 'exit', 'c', 'close', 'end'):
            # clean exit without errors
            code = EXIT_CLEAN
            looping = False
        # the user is an idiot
        else:
            print(colors.alert() + '\nThat wasn\'t an option. Try again.\n' + colors.end())
    
    if not optionsList[6] == None:
        optionsList[6].close()
    
    if code == None:
        return EXIT_UNKNOWN_ERROR
    else:
        return code

## This method calls the search programs main method and also gracefully terminates the program upon completion, displaying
# a return code (0 is good, anything else is bad).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
