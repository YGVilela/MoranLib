"""
get_fixation_stats.py

This script generates fixation statistics for simple Moran simulations based on the specified parameters.

Usage:
    python3 get_fixation_stats.py [-r INSTANCE_REGEX] [-f FOLDER]

Arguments:
    -r, --instanceRegex: Regular expression to filter the simulations that should be analysed. Default is '.*'.
    -f, --folder: Main folder to save the stats. Default is the one set in env.
"""

import argparse
from datetime import datetime
from os import path, makedirs

from pandas import DataFrame

from env import Env
from src.db.simpleMoranDb import SimpleMoranInstanceData
from src.misc.bars import SimpleBar

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--instanceRegex", help="Regular expression to filter the simulations that should be analysed. Default is '.*'", default=".*")
parser.add_argument(
    "-f", "--folder", help="Main folder to save the stats. Default is the one set in env.", 
    default=path.join(Env.DATA_FOLDER.name, Env.STATS_FOLDER.name)
)

args = parser.parse_args()
instanceRegex = args.instanceRegex
mainFolder = args.folder

# Init folder
makedirs(mainFolder, exist_ok=True)
timestamp = int(round(datetime.now().timestamp()))
saveFolder = path.join(mainFolder, str(timestamp))
makedirs(saveFolder, exist_ok=True)

# Load data
instanceNames = SimpleMoranInstanceData.list_instances(instanceRegex)
bar = SimpleBar(len(instanceNames))
allExecutionData = []
for name in instanceNames:
    print(f"Loading {name} data.")
    instance = SimpleMoranInstanceData.load_instance(name)

    label = f"{instance.params.name}_{instance.initialPopulation}"
    lastStep = instance.lastStep
    fixatedIndex = instance.fixatedIndex

    allExecutionData.append({
        "label": label,
        "lastStep": lastStep,
        "fixatedIndex": fixatedIndex
    })

    bar.tick()

df = DataFrame(allExecutionData)
# Group data by label
groupedData = df.groupby(by="label")

# Calculate stats for for "lastStep"
lastStep_stats = groupedData['lastStep'].agg(['mean', 'std', 'max', 'min']).add_prefix('lastStep_')

# Count occurrences of each value in "fixatedIndex"
fixated_index_counts = groupedData['fixatedIndex'].value_counts().unstack(fill_value=0).add_prefix('fixated_index_')

# Merge summary statistics and fixed index counts
result = lastStep_stats.merge(fixated_index_counts, how='left', left_index=True, right_index=True)

# Reset index to include 'label' as a column
result.reset_index(inplace=True)

# Save csv
generalStatsFile = path.join(saveFolder, "generalStats.csv")
result.to_csv(generalStatsFile, index=False)
print(f"General stats saved to {generalStatsFile}")