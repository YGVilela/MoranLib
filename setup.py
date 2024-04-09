"""
This script initializes the necessary folder structure for the Moran simulations.

It reads environment variables to determine the folder paths and creates the necessary directories accordingly.

Usage:
    python3 setup.py

Environment Variables:
    DATA_FOLDER: Root folder where all data will be stored.
    MORAN_PARAMS_FOLDER: Subfolder to store general parameters for the Moran Process.
    SIMULATION_INSTANCES_FOLDER: Subfolder to store the state of the simulations.
    CYCLE_DATA_FOLDER: Subfolder to store actual simulation data.
    STATS_FOLDER: Subfolder to store the simulations stats.

Description:
    This script initializes a folder structure to store data related to Moran process simulations.
    It reads environment variables to determine the folder paths.
    The script performs the following steps:
    1. Loads environment variables using dotenv.
    2. Prints the folder structure for safety.
    3. Creates the root folder if it doesn't exist.
    4. Creates subfolders for Moran parameters, simulation instances, cycle data, and simulation stats.
"""


from os import environ, path, makedirs
from dotenv import load_dotenv

from src.misc.bars import CountdownBar

# Load configuration from .env
load_dotenv()
dataFolder = environ.get("DATA_FOLDER")
moranParamsFolder = environ.get("MORAN_PARAMS_FOLDER")
simInstancesFolder = environ.get("SIMULATION_INSTANCES_FOLDER")
cycleDataFolder = environ.get("CYCLE_DATA_FOLDER")
statsFolder = environ.get("STATS_FOLDER")

def create_folder_structure():
    # Create the root folder
    makedirs(dataFolder, exist_ok=True)

    # Create subfolders
    sim_params_path = path.join(dataFolder, moranParamsFolder)
    cycle_data_path = path.join(dataFolder, cycleDataFolder)
    sim_instance_path = path.join(dataFolder, simInstancesFolder)
    stats_path = path.join(dataFolder, statsFolder)

    # Create subfolders
    makedirs(sim_params_path, exist_ok=True)
    makedirs(cycle_data_path, exist_ok=True)
    makedirs(sim_instance_path, exist_ok=True)
    makedirs(stats_path, exist_ok=True)

def print_folder_structure():    
    print(dataFolder)
    print(f"|-- {moranParamsFolder}\t\t # General parameters for the Moran Process")
    print(f"|-- {simInstancesFolder}\t # Simulation state info")
    print(f"|-- {cycleDataFolder}\t\t # Actual simulation data")
    print(f"|-- {statsFolder}\t\t # Simulations stats")

# Safety check
print("Creating data folders with structure:")
print_folder_structure()
CountdownBar(5).start()

# Go!
create_folder_structure()