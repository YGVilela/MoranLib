"""
setup.py

This script creates the folder structure for a data storage system based on the configuration specified in the Env class.

Usage:
    python3 setup.py

"""

from os import path, makedirs

from env import Env
from src.misc.bars import CountdownBar


# Load variables
mainFolder = Env.DATA_FOLDER.name
subfolders = Env.SUBFOLDERS

def create_folder_structure():
    # Create the root folder
    makedirs(mainFolder, exist_ok=True)

    # Create subfolders
    for sf in subfolders:
        makedirs(path.join(mainFolder, sf.name), exist_ok=True)


def print_folder_structure():    
    print(mainFolder)

    max_folder_length = max(len(item.name) for item in subfolders)
    for sf in subfolders:
        print(f"|-- {sf.name.ljust(max_folder_length)}\t\t # {sf.description}")
        
# Safety check
print("Creating data folders with structure:")
print_folder_structure()
CountdownBar(5).start()

# Go!
create_folder_structure()