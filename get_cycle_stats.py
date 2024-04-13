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
from src.db.composedMoranDbDb import CycleData, ComposedMoranInstanceData

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
        allCycleData.append({
            "params": instance.params.name,
            "initialPopulation": f"{instance.initialPopulation}",
            "cycleNumber": cycleNumber,
            "x1": cycleData.finalPopulation[0],
            "x2": cycleData.finalPopulation[1],
            "x3": cycleData.finalPopulation[2],
            "diffX1": cycleData.finalPopulation[0] - instance.initialPopulation[0],
            "diffX2": cycleData.finalPopulation[1] - instance.initialPopulation[1],
            "diffX3": cycleData.finalPopulation[2] - instance.initialPopulation[2],
        })

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
    paramStatsFolder = path.join(saveFolder, params, f"{initialPopulation}")
    makedirs(paramStatsFolder, exist_ok=True)

    # Final points
    finalPoints = (groupedData.get_group(group)[["x1", "x2", "x3"]]).to_numpy().tolist()
    finalPointsFile = path.join(paramStatsFolder, f"finalPoints_{cycleNumber}.json")
    with open(finalPointsFile, "w") as file:
        json.dump(finalPoints, file)
    print(f"Final points of {group} saved to {finalPointsFile}")

    # Histogram data
    size = sum(eval(initialPopulation))
    x1HistData = (groupedData.get_group(group)["x1"]/size).value_counts(bins=intervals, sort=False, normalize=True)
    x2HistData = (groupedData.get_group(group)["x2"]/size).value_counts(bins=intervals, sort=False, normalize=True)
    x3HistData = (groupedData.get_group(group)["x3"]/size).value_counts(bins=intervals, sort=False, normalize=True)

    fig, axs = subplots(3, 1, figsize=(9, 9), sharex=True)
    axs[0].bar(x1HistData.index.mid, x1HistData.values, width=delta, align='center', color="blue")
    axs[0].set_ylim([0, 1])
    axs[0].set_title('')
    axs[0].legend(["x1"])

    axs[1].bar(x2HistData.index.mid, x2HistData.values, width=delta, align='center', color="green")
    axs[1].set_ylim([0, 1])
    axs[1].set_title('')
    axs[1].legend(["x2"])

    axs[2].bar(x3HistData.index.mid, x3HistData.values, width=delta, align='center', color="orange")
    axs[2].set_ylim([0, 1])
    axs[2].set_title('')
    axs[2].legend(["x3"])

    allHistFile = path.join(paramStatsFolder, f"histograms_{cycleNumber}.png")
    fig.savefig(allHistFile, bbox_inches='tight')
    
    close(fig)
    print(f"Histograms for {group} saved to {allHistFile}.")
    bar.tick()
