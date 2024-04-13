"""
execute_simple_moran.py

This script executes simple Moran simulations until fixation based on the specified parameters.

Usage:
    python3 execute_simple_moran.py [-r INSTANCE_REGEX] [-t THREADS]

Arguments:
    -r, --instanceRegex: Regular expression to filter the simulations that should be executed. Default is '.*'.
    -t, --threads: Number of threads to be used in the execution. Default is 3.
"""

import argparse
from src.db.simpleMoranDb import SimpleMoranInstanceData
from src.misc.bars import CountdownBar, ParallelBar
from src.core.moranSim import SimpleMoranInstance
from multiprocessing import Pool
from math import floor

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--instanceRegex", help="Regular expression to filter the simulations that should be executed. Default is '.*'", default=".*")
parser.add_argument("-t", "--threads", help="Number of threads to be used in the execution. Default is 3.", default=3, type=int)

args = parser.parse_args()
instanceRegex = args.instanceRegex
threads = args.threads

# Load instances
instanceNames = SimpleMoranInstanceData.list_instances(instanceRegex)

# Safety check
print(f"Executing {len(instanceNames)} simulations until fixation. Is that correct?")
CountdownBar(5).start()

# Init instances and progress bar
# TODO: How can we change to avoid loading all instances at once?
instances = [SimpleMoranInstance.load_instance(name) for name in instanceNames]
totalReps = len(instanceNames)
barSize = totalReps
bar = ParallelBar(barSize)

# Go!
def run(sim: SimpleMoranInstance):
    print(f"Executing {sim.instanceData.name}")

    (lastStep, fixatedIndex) = sim.execute()

    sim.instanceData.save_instance()

    print(f"Ended {sim.instanceData.name} on step {lastStep} with type {fixatedIndex} fixed.")
    bar.tick()

    return 0

with Pool(threads) as pool:
    pool.map(run, instances)

bar.wait()