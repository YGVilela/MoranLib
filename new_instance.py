"""
This script creates multiple simulations using the Moran process with specified parameters.

Usage:
    python script_name.py paramsName initialPopulation [-n SIM_COUNT] [-p NAME_PREFIX]

Arguments:
    paramsName (str): Name of the Moran parameters file to be used.
    initialPopulation (str): Initial population distribution for the simulations.

Options:
    -n SIM_COUNT, --simCount SIM_COUNT
        Number of simulations to be created. Default is 1.

    -p NAME_PREFIX, --namePrefix NAME_PREFIX
        Prefix to be used on the simulation's names. Default is an empty string.

Example:
    python3 new_instance.py stableRoutine "(300, 200, 500)" -n 5
    python3 new_instance.py unstableRoutine "(300, 200, 500)" -n 5

Description:
    This script creates multiple simulations using the Moran process with the specified parameters.
    The Moran parameters file contains the configuration for the simulations.
    The initial population distribution is provided as a JSON-formatted string.
    Additional options allow specifying the number of simulations to create and a prefix for the simulation names.

    The script performs the following steps:
    1. Parses command-line arguments to extract parameters.
    2. Loads Moran parameters from the specified file.
    3. Prints information about the simulations to be created.
    4. Initializes progress bars to track creation progress.
    5. Creates simulation instances based on the parameters.
    6. Displays progress bars until all simulations are completed.
"""


from json import loads
import argparse
from textwrap import wrap

from src.misc.bars import CountdownBar, ParallelBar
from src.db.moranDb import RoutineParams, InstanceData
from datetime import datetime
from math import floor

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("paramsName", help="Name of the Moran parameters file to be used.")
parser.add_argument("initialPopulation", help="Initial population distribution for the simulations.")
parser.add_argument("-n", "--simCount", help="Number of simulations to be created. Default is 1.", default=1, type=int)
parser.add_argument("-p", "--namePrefix", help="Prefix to be used on the simulation's names. Default is an empty string.", default="")

args = parser.parse_args()

paramsName = args.paramsName
initialPopulation = loads(
    args.initialPopulation
    .replace("(", "[")
    .replace(")", "]")
)
simCount = args.simCount
namePrefix = f"{args.namePrefix}_" if args.namePrefix != "" else ""

# Safety check
params = RoutineParams.load_params(paramsName)
timestamp = int(round(datetime.now().timestamp()))
baseName = f"{namePrefix}{params.name}_{timestamp}"

print(f"Creating {simCount} simulations of {paramsName} with initial population {initialPopulation}.\n")
print(f"Simulation(s) will be named as {baseName}_*.\n")
print("\n".join(wrap(f"\"{params.description}\"")))
print("\nIs that correct?")
CountdownBar(5).start()

# Bar setup
barSize = floor(simCount)
bar = ParallelBar(barSize)

# Go!
for index in range(simCount):
    instanceName = f"{baseName}_{index}"
    instanceData = InstanceData.create_instance(paramsName, initialPopulation, instanceName)
    bar.tick()

bar.wait()
print(f"Created {simCount} simulations with name {baseName}_*.")