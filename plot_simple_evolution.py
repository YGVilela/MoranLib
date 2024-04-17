"""plot_simple_evolution.py

This script plots the mean evolution of several simple Moran instances with error bars.

Usage:
    python3 plot_simple_evolution.py [-f FOLDER] [-s SAMPLESIZE] [-m MAXSTEP] (-j JSONARRAY | -l LIST | -r INSTANCEREGEX)

Arguments:
    -f FOLDER, --folder FOLDER: Main folder to save the stats. Default is the one set in env.
    -s SAMPLESIZE, --sampleSize SAMPLESIZE: Number of points to consider on each simulation. Default is 200.
    -m MAXSTEP, --maxStep MAXSTEP: Maximum step to be considered on the simulations. Default is 100000.
    -j JSONARRAY, --jsonArray JSONARRAY: JSON file containing an array with the names of the instances to be considered.
    -l LIST, --list LIST:  Names of the instances to be considered.
    -r INSTANCEREGEX, --instanceRegex INSTANCEREGEX: Regular expression to filter the simulations that should be analysed.
"""


import argparse
from datetime import datetime
import json
from math import floor
from os import makedirs, path
from pandas import DataFrame
import matplotlib.pyplot as plt
from numpy import arange, mean, std

from env import Env
from src.misc.bars import SimpleBar
from src.db.simpleMoranDb import IterationData, SimpleMoranInstanceData

def isComparable(instanceData):
    paramName = instanceData[0].params.name
    initialPopulation = instanceData[0].initialPopulation

    for data in instanceData:
        if paramName != data.params.name:
            print(f"Different params: {paramName} and {data.params.name}")
            return False
        if initialPopulation != data.initialPopulation:
            print(f"Different initial populations: {initialPopulation} and {data.initialPopulation}")
            return False

    return True

def update_max_step(summarizedInfo, currMax):
    # Last step with info on ALL simulations
    lastInfo = currMax

    # Last step with relevant info on SOME simulation
    lastRelevant = 0

    for data in summarizedInfo:
        # If not fixated, last info is on lastStep
        if data.fixatedIndex is None and data.lastStep < lastInfo:
            lastInfo = data.lastStep

        # Last relevant info always on the last step
        if data.lastStep > lastRelevant:
            lastRelevant = data.lastStep

    # As last info starts with currMax and decreases, this is smallar than currMax
    return min(lastInfo, lastRelevant)

def load_sample(instanceName, sampleIndexes, callback):
    allData = IterationData.load_iteration_data_from_name(instanceName)
    instanceMax = len(allData)
    samplePoints = [
        allData[index] if index < instanceMax else allData[instanceMax -1]
        for index in sampleIndexes
    ]
    callback()

    return samplePoints

def plot_evolution_with_errorbars(coordinates, sampleIndexes, fileName):
    lastColumn = len(sampleIndexes)

    # Assemble columns
    columns = [
        [coordinates[i][j] for i in range(len(coordinates)) if j < len(coordinates[i])]
        for j in range(lastColumn)
    ]

    # Calculate mean and standard deviation for each coordinate
    means = DataFrame([mean(col, axis=0) for col in columns])
    stds = DataFrame([std(col, axis=0) for col in columns])

    # Plot mean with error bars for standard deviation
    dimension = len(coordinates[0][0])
    fig, axs = plt.subplots(dimension, 1, figsize=(floor(lastColumn/10), 9), sharex=True)
    colors = ["blue", "green", "orange"]
    for i in range(dimension):
        axs[i].errorbar(sampleIndexes, means[i], yerr=stds[i], label=f'Coordinate {i+1}', fmt='-o', color=colors[i%len(colors)])
        axs[i].set_title('')
        axs[i].legend([f"x{i + 1}"])

    fig.savefig(fileName, bbox_inches='tight')
    plt.close(fig)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f", "--folder", help="Main folder to save the stats. Default is the one set in env.", 
    default=path.join(Env.DATA_FOLDER.name, Env.STATS_FOLDER.name)
)
parser.add_argument("-s", "--sampleSize", help="Number of points to consider on each simulation. Default is 200.", default=200)
parser.add_argument("-m", "--maxStep", help="Maximum step to be considered on the simulations. Default is 100000.", default=100000)

simList = parser.add_mutually_exclusive_group(required=True)
simList.add_argument("-j", "--jsonArray", help="JSON file containing an array with the names of the instances to be considered.")
simList.add_argument("-l", "--list", action="append", help="Names of the instances to be considered.")
simList.add_argument("-r", "--instanceRegex", help="Regular expression to filter the simulations that should be analysed.")

args = parser.parse_args()

instanceList = None
if args.list is not None:
    instanceList = args.list
elif args.jsonArray is not None:
    file = open(args.jsonArray, mode="r")
    instanceList = json.load(file)
    file.close()
elif args.instanceRegex is not None:
    instanceList = SimpleMoranInstanceData.list_instances(args.instanceRegex)
else:
    raise Exception("Can't list instances.")

sampleSize = args.sampleSize
maxStep = args.maxStep
mainFolder = args.folder

# Load summarized info
summarizedInfo = [SimpleMoranInstanceData.load_instance(name) for name in instanceList]

# Check if all instances have the same params and initial condition
if not isComparable(summarizedInfo):
    raise Exception("Can't compare instances with different params or initial condition.")

# Update max step: considering the following
## - If an instance is fixated, we can get real data even after it is finished, but it won't be relevant
## - If an instance is not fixated, we can't get real data after the last step that was simulated
## Max step must be the maximum step we can get real and relevant data for all sims
print("Updating max steps.")
maxStep = update_max_step(summarizedInfo, maxStep)

# Reduce steps based on sampleSize
if sampleSize > maxStep:
    print(f"Not enought points to sample {sampleSize}. Reducing to {maxStep}")
    maxStep = sampleSize

# Get graph data
print("Loading data")
sampleIndexes = arange(0, maxStep, floor(maxStep/sampleSize))
loadBar = SimpleBar(len(instanceList))
itData = [
    load_sample(name, sampleIndexes, loadBar.tick)
    for name in instanceList
]

# Create folder to save the data
timestamp = int(round(datetime.now().timestamp()))
saveFolder = path.join(mainFolder, f"{timestamp}")
makedirs(saveFolder, exist_ok=True)

# Save stats graph
fileName = path.join(saveFolder, "statsGraph.png")
plot_evolution_with_errorbars(itData, sampleIndexes, fileName)
print(f"Graph saved on {fileName}")
