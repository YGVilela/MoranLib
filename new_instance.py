"""
new_instances.py

This script creates new instances of Moran simulations based on the specified parameters and initial population distribution.

Usage:
    python3 new_instances.py paramsName initialPopulation [-n SIM_COUNT] [-p NAME_PREFIX]

Arguments:
    paramsName: Name of the Moran parameters file to be used.
    initialPopulation: Initial population distribution for the simulations.
    -n, --simCount: Number of simulations to be created. Default is 1.
    -p, --namePrefix: Prefix to be used on the simulation's names. Default is an empty string.
"""


from json import loads
import argparse
from textwrap import wrap

from src.db.utils import load_params, get_instance_data_class
from src.misc.bars import CountdownBar, ParallelBar
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
params = load_params(paramsName)
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
    get_instance_data_class(params.simType).create_instance(paramsName, initialPopulation, instanceName)
    bar.tick()

bar.wait()
print(f"Created {simCount} simulations with name {baseName}_*.")