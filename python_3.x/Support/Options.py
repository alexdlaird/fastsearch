#!/usr/bin/env python

# system modules
import ftplib, getpass, re, os

# my modules
import FileHandler, Output

## This module contains the methods that allow the users to specify specific options for the search.
#
# @file Options.py
# @version 1.2

## Checks to see if the given string is a valid remote connection.
#
# @param string A remote connection path.
# @return True if the given string was a valid connection, False otherwise.
def isValidRemoteConn(string):
    if string.startswith('ftp://') or string.startswith('ftp.'):
        string = string.replace('ftp://', '')
        if not string.find('/') == -1:
            string = string[:string.find('/')]
        try:
            ftplib.FTP(string)
            return True
        except:
            return False
    else:
        return -1

## Checks to see if the given username and password are valid for the given connection.
#
# @param address The remote connection path.
# @param username The username to login to the remote server.
# @param password The password to login to the remote server.
# @return True if the login is valid, False otherwise.
def isValidLogin(address, username, password):
    try:
        ftp = ftplib.FTP(address)
        ftp.login(username, password)
        return True
    except:
        return False

## This method presents the user with a list of enhanced features that they can use when searching.
#
# @param fastSearchDir The path of FastSearch.
# @param optionsList The list of current option values.
# @return The list of new option values.
def options(fastSearchDir, optionsList, colors):
    Output.options(optionsList, colors)
    
    # loop until the user wants to go back
    while True:
        # capture the users choice
        string = input(colors.cyan() + 'Enter an option: ' + colors.end()).lower()

        # the user wants to enable or disable a deep search
        if string in ('d', 'deep', 'deep search', 'ds'):
            optionsList[0] = not optionsList[0]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Deep Search is now %s' % (optionsList[0] and 'on' or 'off') + '...\n' + colors.end())
        # the user wants only files to be displayed in the results
        elif string in ('i', 'file', 'files', 'file only', 'files only', 'only file', 'only files'):
            optionsList[1] = 0
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will now only include files...\n' + colors.end())
        # the user wants only folders to be displayed in the results
        elif string in ('e', 'folder', 'folders', 'folder only', 'folders only', 'only folder', 'only folders'):
            optionsList[1] = 1
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will now only include folders...\n' + colors.end())
        # the user wants both files and folders to be displayed in the results
        elif string in ('o', 'both', 'both file and foler', 'both files and folder', 'both file and folders', 'both files and folders', 'file and folder', \
                        'files and folder', 'file and folders', 'files and folders', 'bff'):
            optionsList[1] = 2
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will now include both files and folders...\n' + colors.end())
        # the user wants to enable or disable the display of hidden files and folders in the results
        elif string in ('h', 'hidden', 'show hidden', 'show hidden file', 'show hidden files', 'show hidden folder', 'show hidden folders', \
                        'hidden file and folder', 'hidden files and folder', 'hidden file and folders', 'hidden files and folders', 'show hidden file and folder', \
                        'show hidden files and folder', 'show hidden file and folders', 'show hidden files and folders', 'hide file', 'hide files', \
                        'hide folder', 'hide folders', 'hide file and folder', 'hide files and folder', 'hide file and folders', 'hide files and folders'):
            optionsList[2] = not optionsList[2]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will %s show hidden files and folders' % (optionsList[2] and 'now' or 'no longer') + '...\n' + colors.end())
        # the user wants the absolute path to be shown in the search results
        elif string in ('f', 'full path', 'abs', 'absolute', 'abspath', 'abs path', 'absolute path'):
            optionsList[3] = 0
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will now show the full (absolute) path...\n' + colors.end())
        # the user wants the relative path to be shown in the search results
        elif string in ('r', 'rel', 'relative', 'relpath', 'rel path', 'relative path'):
            optionsList[3] = 1
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will now show the relative path...\n' + colors.end())
        # the user doesn't want the path shown in the search results
        elif string in ('n', 'no path'):
            optionsList[3] = 2
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Search results will no longer show a path...\n' + colors.end())
        # the user wants to enable or disable a full search
        elif string in ('u', 'full search', 'partial', 'partial search'):
            optionsList[4] = not optionsList[4]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Full Search is now %s' % (optionsList[4] and 'on' or 'off') + '...\n' + colors.end())
        # the user wants to change the root directory
        elif string in ('dir', 'directory', 'r', 'root', 'rootdir', 'root dir', 'root directory', 'curdir', 'cur dir', 'cur directory', 'current directory'):
            string = input(colors.cyan() + 'Enter the path for the new root director: ' + colors.end())
            # ensure that the user has given a valid new root directory
            if os.path.exists(string):
                optionsList[5] = string
                if not optionsList[6] == None:
                    optionsList[6].close()
                optionsList[6] = None
                FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
                print(colors.alert() + '...The new root directory is ' + optionsList[5] + '...\n' + colors.end())
            # if the directory isn't local, perhaps it is an ftp location
            elif isValidRemoteConn(string):
                string = string.replace('ftp://', '')
                if not string.startswith('ftp.'):
                    string = 'ftp.' + string
                localDir = None
                if not string.find('/') == -1:
                    address = string[:string.find('/')]
                    localDir = string[string.find('/'):]
                else:
                    address = string
                username = input(colors.cyan() + 'Username: ' + colors.end())
                password = getpass.getpass(colors.cyan() + 'Password: ' + colors.end())
                if isValidLogin(address, username, password):
                    temp = optionsList[5]
                    optionsList[5] = address
                    ftp = ftplib.FTP(address)
                    ftp.login(username, password)
                    if not localDir == None or (not localDir == None and localDir.strip() == ''):
                        try:
                            ftp.cwd(localDir)
                            optionsList[5] += localDir
                        except:
                            optionsList[5] = temp
                            print(colors.error() + 'The remote server was valid, but the specified local directory, ' + localDir + ', could not be found.' \
                                  + '\nCheck your spelling, verify that the directory exists, and try again. The root directory has not changed.' + colors.end())
                            print(colors.alert() + '...The root directory remains ' + optionsList[5] + '...\n' + colors.end())
                            continue
                    if not optionsList[6] == None:
                        optionsList[6].close()
                    optionsList[6] = ftp
                    print(colors.alert() + '...The new root directory is ' + optionsList[5] + '...\n' + colors.end())
                else:
                    print(colors.error() + 'The username or password did match any accounts on ' + string + '. The root directory has not changed.' + colors.end())
                    print(colors.alert() + '...The root directory remains ' + optionsList[5] + '...\n' + colors.end())
            else:
                if isValidRemoteConn(string) == -1:
                    print(colors.error() + 'The path specified was not a valid directory. The root directory has not changed.' + colors.end())
                    print(colors.alert() + '...The root directory remains ' + optionsList[5] + '...\n' + colors.end())
                else:
                    print(colors.error() + 'The remote server specified may have been valid, but a connection could not be made.\nCheck your internet ' \
                          + 'connection and try again. The root directory has not changed.' + colors.end())
                    print(colors.alert() + '...The root directory remains ' + optionsList[5] + '...\n' + colors.end())
        # store recent search results
        elif string in ('s', 'save', 'save recent', 'save recent search', 'save recent searches', 'save search', 'save searches', 'save history', \
            'recent', 'recent searches', 'recent search', 'history'):
            optionsList[8] = not optionsList[8]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Recent search results will %s be stored in RecentSearches.txt' % (optionsList[8] and 'now' or 'no longer') + '...\n' + colors.end())
        # the user wants the screen to clear
        elif string in ('c', 'clear', 'clear screen', 'clear shell', 'clear console', 'clear terminal', 'cls', 'clr'):
            optionsList[7] = not optionsList[7]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...The screen will %s clear the screen before display search results' % (optionsList[7] and 'now' or 'no longer') + '...\n' + colors.end())
        # the user wants to change the thread count
        elif string in ('t', 'thread', 'threads', 'threads used', 'thread used', 'thread count', 'threads count', 'num thread', 'num threads', 'number thread', \
            'number threads', 'num of thread', 'num of threads', 'number of thread', 'number of threads'):
            string = input(colors.cyan() + 'Enter the number of threads to split the search into: ' + colors.end())
            # ensure that the user entered an interger
            try:
                optionsList[9] = int(string)
                FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
                print(colors.alert() + '...The search will no be split into ' + str(optionsList[9]) + ' threads...\n' + colors.end())
            except:
                print(colors.error() + 'You did not specify a valid integer for the new thread count.' + colors.end())
                print(colors.alert() + '...The thread count remains at ' + str(optionsList[9]) + '...\n' + colors.end())
        # the user wants no animations shown
        elif string in ('no anim', 'no anims', 'no animation', 'no animations', 'disable anim', 'disable anims', 'disable animation', 'disable animations', 'disable all anim', \
            'disable all anims', 'disable all animation', 'disable all animations', 'disable full anim', 'disable full anims', 'disable full animation', 'disable full animations'):
            optionsList[10] = 0
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...No search animations will be displayed...\n' + colors.end())
        # the user wants only the pinwheel animation shown
        elif string in ('p', 'pinwheel', 'show pinwheel', 'show pinwheel only', 'pinwheel anim', 'pinwheel animation', 'show pinwheel anim', 'show pinwheel animation', \
            'show pinwheel anim only', 'show pinwheel animation only', 'show only pinwheel', 'show only pinwheel anim', 'show only pinwheel animation', 'only pinwheel anim', \
            'only pinwheel animation', 'only pinwheel'):
            optionsList[10] = 1
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...Only the pinwheel search animation will be displayed...\n' + colors.end())
        # the user wants all animations shown
        elif string in ('a', 'anim', 'anims', 'animation', 'animations', 'all anim', 'all anims', 'all animation', 'all animations', 'show anim', 'show anims', 'show animation', \
            'show animations', 'show all anim', 'show all anims', 'show all animation', 'show all animations', 'full anim', 'full anims', 'full animation', 'full animations', \
            'show full anim', 'show full anims', 'show full animation', 'show full animations', 'enable anim', 'enable anims', 'enable all anim', 'enable all anims', \
            'enable all animation', 'enable all animations', 'enable full anim', 'enable full anims', 'enable full animation', 'enable full animations', 'enable search anim', \
            'enable search anims', 'enable search animation', 'enable search animations', 'enable full search anim', 'enable full search anims', 'enable full search animation', \
            'enable full search animations', 'enable all search anim', 'enable all search anims', 'enable all search animation', 'enable all search animations'):
            optionsList[10] = 2
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            print(colors.alert() + '...All search animations will be displayed...\n' + colors.end())
        # the user does not want to display text
        elif string in ('x', 'color', 'coloring', 'colors', 'show colors', 'show text colors', 'show color', 'show text color', 'text color', 'text', 'text colors', \
            'text coloring', 'show coloring', 'show text coloring'):
            optionsList[11] = not optionsList[11]
            FileHandler.writeNewOptionsList(fastSearchDir, optionsList, True)
            colors.setColors(optionsList)
            print(colors.alert() + '...Text coloring will %s be used' % (optionsList[11] and 'now' or 'no longer') + '...\n' + colors.end())
        elif string in ('show', 'show again', 'show menu', 'menu', 'display', 'display menu', 'option', 'options', 'option menu', 'options menu', 'show option', 'show options'):
            return options(fastSearchDir, optionsList)
        # the user wants to go back to the main menu
        elif string in ('b', 'back', 'go back', 'close', 'q', 'quit', 'exit'):
            print(colors.cyan() + '\n--------------------------\n' + colors.end())
            return optionsList
        # the user is an idiot
        else:
            print(colors.alert() + '\nThat wasn\'t an option. Try again.\n' + colors.end())
