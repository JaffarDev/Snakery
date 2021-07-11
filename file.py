#File.py
#Module to deal with files

import os
import sys
import pathlib

#Locates the given resource's path, which may be in the user's temp folder or in the project's root directory
#This method is used specifically for pyinstaller, in order to find the program's resource files when launched from an executable
#This method also ensures that resource folders are located when the program is run from a development environment
def locate(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

#Creates a directory and any required parents if it does not already exist
def verify_dir(path):
    pathlib.Path(path).mkdir(parents = True, exist_ok = True)


