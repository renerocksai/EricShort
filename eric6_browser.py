#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2016 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Eric6 Web Browser.

This is the main Python script that performs the necessary initialization
of the web browser and starts the Qt event loop. This is a standalone version
of the integrated web browser. It is based on QtWebEngine.
"""

from __future__ import unicode_literals

import Toolbox.PyQt4ImportHook  # __IGNORE_WARNING__

try:  # Only for Py2
    import Globals.compatibility_fixes     # __IGNORE_WARNING__
except (ImportError):
    pass

try:
    import sip
    sip.setdestroyonexit(False)
except AttributeError:
    pass

import sys
import os

# TODO: adjust this to 5.6.0 when done
MIN_QT_VERSION = "5.5.0"

from PyQt5.QtCore import qVersion
if qVersion() < MIN_QT_VERSION:
    try:    # Py2
        import tkMessageBox as messagebox
    except ImportError:
        try:    # Py3
            from tkinter import messagebox
        except ImportError:
            sys.exit(100)
    messagebox.showerror(
        "eric6 Error",
        "You need at least Qt Version {0} to execute the web browser."
          .format(MIN_QT_VERSION))
    sys.exit(100)

SettingsDir = None

for arg in sys.argv[:]:
    if arg.startswith("--config="):
        import Globals
        configDir = arg.replace("--config=", "")
        Globals.setConfigDir(configDir)
        sys.argv.remove(arg)
    elif arg.startswith("--settings="):
        from PyQt5.QtCore import QSettings
        SettingsDir = os.path.expanduser(arg.replace("--settings=", ""))
        if not os.path.isdir(SettingsDir):
            os.makedirs(SettingsDir)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                          SettingsDir)
        sys.argv.remove(arg)

# make ThirdParty package available as a packages repository
sys.path.insert(2, os.path.join(os.path.dirname(__file__),
                                "ThirdParty", "Pygments"))

from PyQt5 import QtWebEngineWidgets    # __IGNORE_WARNING__

import Globals
from Globals import AppInfo

from Toolbox import Startup


def createMainWidget(argv):
    """
    Function to create the main widget.
    
    @param argv list of commandline parameters (list of strings)
    @return reference to the main widget (QWidget)
    """
    from WebBrowser.WebBrowserWindow import WebBrowserWindow
    
    searchWord = None
    private = False
    for arg in reversed(argv):
        if arg.startswith("--search="):
            searchWord = argv[1].split("=", 1)[1]
            argv.remove(arg)
        elif arg == "--private":
            private = True
            argv.remove(arg)
        elif arg.startswith("--"):
            argv.remove(arg)
    
    try:
        home = argv[1]
    except IndexError:
        home = ""
    
    browser = WebBrowserWindow(home, '.', None, 'web_browser',
                               searchWord=searchWord, private=private,
                               settingsDir=SettingsDir)
    return browser


def main():
    """
    Main entry point into the application.
    """
    options = [
        ("--config=configDir",
         "use the given directory as the one containing the config files"),
        ("--private",  "start the browser in private browsing mode"),
        ("--search=word", "search for the given word"),
        ("--settings=settingsDir",
         "use the given directory to store the settings files"),
    ]
    appinfo = AppInfo.makeAppInfo(sys.argv,
                                  "eric6 Web Browser",
                                  "file",
                                  "web browser",
                                  options)
    
    if not Globals.checkBlacklistedVersions():
        sys.exit(100)
    
    res = Startup.simpleAppStartup(sys.argv,
                                   appinfo,
                                   createMainWidget,
                                   installErrorHandler=True)
    sys.exit(res)

if __name__ == '__main__':
    main()
