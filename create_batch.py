"""
create_batch.py

This script creates a batch of Moran simulations according to parameters specified on a json.

Usage:
    python3 create_batch.py batchParamsFile.json

Arguments:
    batchParams: Name of the parameters for the batch.
"""


from datetime import datetime
from json import load
from sys import argv
from tabulate import tabulate

from src.db.utils import get_instance_data_class, load_params
from src.misc.bars import CountdownBar, SimpleBar

file = open(argv[1])
params = load(file)
for entry in params:
    totalPop = sum(entry["initialPopulation"])
    entry["populationFraction"] = [ pop/totalPop for pop in entry["initialPopulation"] ]
    entry["totalPopulation"] = totalPop

# Sumarize operation
totalSimCount = sum([entry["simCount"] for entry in params])
timestamp = int(round(datetime.now().timestamp()))
print(f"Creating {totalSimCount} sims with suffix '.*_{timestamp}_.*':\n")
print(tabulate(params, headers="keys"))
print("\nIs that correct?")
CountdownBar(10).start()

# Go!
bar = SimpleBar(totalSimCount)
for entry in params:
    currSimParams = load_params(entry["paramsName"])
    currSimCount = entry["simCount"]
    currNamePrefix = entry["namePrefix"]
    baseName = baseName = f"{currNamePrefix}_{currSimParams.name}_{timestamp}"
    for index in range(currSimCount):
        instanceName = f"{baseName}_{index}"
        get_instance_data_class(currSimParams.simType).create_instance(currSimParams.name, entry["initialPopulation"], instanceName)
        bar.tick()

    print(f"Created {currSimCount} simulations of {currSimParams.name} with name {baseName}_*.")

