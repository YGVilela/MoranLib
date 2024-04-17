"""
get_cycle_stats.py

This script generates cycle statistics for composed Moran simulations based on the specified parameters and analysis options.

Usage:
    python3 get_cycle_stats.py [-r INSTANCE_REGEX] [-f FOLDER] [-d DELTA]

Arguments:
    -r, --instanceRegex: Regular expression to filter the simulations that should be analysed. Default is '.*'.
    -f, --folder: Main folder to save the stats. Default is the one set in env.
    -d, --delta: Length of the histograms intervals. Default is 0.02.
"""

import argparse
from datetime import datetime
import json
from os import path, makedirs
from numpy import arange

from pandas import DataFrame
from matplotlib.pyplot import subplots, close

from env import Env
from src.misc.bars import SimpleBar
from src.db.composedMoranDb import CycleData, ComposedMoranInstanceData

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--instanceRegex", help="Regular expression to filter the simulations that should be analysed. Default is '.*'", default=".*")
parser.add_argument(
    "-f", "--folder", help="Main folder to save the stats. Default is the one set in env.", 
    default=path.join(Env.DATA_FOLDER.name, Env.STATS_FOLDER.name)
)
parser.add_argument("-d", "--delta", help="Length of the histograms intervals. Default is 0.02", default=0.02, type=float)

args = parser.parse_args()
instanceRegex = args.instanceRegex
mainFolder = args.folder
delta = args.delta

# Load data
instanceNames = ComposedMoranInstanceData.list_instances(instanceRegex)
bar = SimpleBar(len(instanceNames))
allCycleData = []
for name in instanceNames:
    print(f"Loading {name} data.")
    instance = ComposedMoranInstanceData.load_instance(name)
    for cycleNumber in range(instance.currentCycle):
        cycleData = CycleData.load_summarized_data(instance.name, cycleNumber)
        relevantData = {
            "params": instance.params.name,
            "initialPopulation": f"{instance.initialPopulation}",
            "cycleNumber": cycleNumber
        }
        for index in range(len(cycleData.finalPopulation)):
            relevantData[f"x{index+1}"] = cycleData.finalPopulation[index]
            relevantData[f"diffX{index+1}"]  = cycleData.finalPopulation[index] - cycleData.initialPopulation[index]

        allCycleData.append(relevantData)

    bar.tick()

df = DataFrame(allCycleData)

# Group data by params, size and cycle number
groupedData = df.groupby(by=["params", "initialPopulation", "cycleNumber"])

# Init folder
makedirs(mainFolder, exist_ok=True)
timestamp = int(round(datetime.now().timestamp()))
saveFolder = path.join(mainFolder, str(timestamp))
makedirs(saveFolder, exist_ok=True)

# General stats
generalStatsFile = path.join(saveFolder, "generalStats.csv")
generalStats = groupedData.describe()
generalStats.to_csv(generalStatsFile)
print(f"General stats saved to {generalStatsFile}")

# Histogram intervals
intervals = arange(0, 1, delta)

# Relevant plots
bar = SimpleBar(len(groupedData.groups))
for group in groupedData.groups:
    # Save stats on that group's param folder
    (params, initialPopulation, cycleNumber) = group
    paramStatsFolder = path.join(saveFolder, params, initialPopulation)
    makedirs(paramStatsFolder, exist_ok=True)

    # Final points
    pointVars = [f"x{index+1}" for index in range(len(eval(initialPopulation)))]
    finalPoints = (groupedData.get_group(group)[pointVars]).to_numpy().tolist()
    finalPointsFile = path.join(paramStatsFolder, f"finalPoints_{cycleNumber}.json")
    with open(finalPointsFile, "w") as file:
        json.dump(finalPoints, file)
    print(f"Final points of {group} saved to {finalPointsFile}")

    # Histogram data
    size = sum(eval(initialPopulation))
    histData = [
        (groupedData.get_group(group)[var]/size).value_counts(bins=intervals, sort=False, normalize=True)
        for var in pointVars
    ]

    fig, axs = subplots(len(histData), 1, figsize=(9, 9), sharex=True)
    colors = ["blue", "green", "orange"]
    for index in range(len(histData)):
        axs[index].bar(histData[index].index.mid, histData[index].values, width=delta, align='center', color=colors[index%len(colors)])
        axs[index].set_ylim([0, 1])
        axs[index].set_title('')
        axs[index].legend([f"x{index + 1}"])

    allHistFile = path.join(paramStatsFolder, f"histograms_{cycleNumber}.png")
    fig.savefig(allHistFile, bbox_inches='tight')
    
    close(fig)
    print(f"Histograms for {group} saved to {allHistFile}.")
    bar.tick()
