"""
resume_composed_moran.py

This script resumes the execution of composed Moran simulations based on the provided configuration and parameters.

Usage:
    python3 resume_composed_moran.py [-r INSTANCE_REGEX] [-n CYCLES_PER_INSTANCE] [-s SAVE_EACH] [-c CALLBACK_EACH] [-t THREADS]

Arguments:
    -r, --instanceRegex: Regular expression to filter the simulations that should be executed. Default is '.*'.
    -n, --cyclesPerInstance: Number of cycles to be executed for each instance. Default is 1.
    -s, --saveEach: Number of steps to be executed between each save. Default is 50000.
    -c, --callbackEach: Number of steps to be executed between each progress bar tick. Default is 1000.
    -t, --threads: Number of threads to be used in the execution. Default is 3.
"""

import argparse
from src.misc.bars import CountdownBar, ParallelBar
from src.core.moranSim import ComposedMoranInstance
from src.db.composedMoranDbDb import ComposedMoranInstanceData
from multiprocessing import Pool
from math import floor

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--instanceRegex", help="Regular expression to filter the simulations that should be executed. Default is '.*'", default=".*")
parser.add_argument("-n", "--cyclesPerInstance", help="Number of cycles to be executed for each instance. Default is 1.", default=1, type=int)
parser.add_argument("-s", "--saveEach", help="Number of steps to be executed between each save. Default is 50000.", default=50000, type=int)
parser.add_argument("-c", "--callbackEach", help="Number of steps to be executed between each progress bar tick. Default is 1000.", default=1000, type=int)
parser.add_argument("-t", "--threads", help="Number of threads to be used in the execution. Default is 3.", default=3, type=int)

args = parser.parse_args()
instanceRegex = args.instanceRegex
cyclesPerInstance = args.cyclesPerInstance
saveEach = args.saveEach
callbackEach = args.callbackEach
threads = args.threads

# Load instances
instanceNames = ComposedMoranInstanceData.list_instances(instanceRegex)

# Safety check
print(f"Executing {len(instanceNames)} simulations {cyclesPerInstance} times. Is that correct?")
CountdownBar(5).start()

# Init instances and progress bar
# TODO: How can we change to avoid loading all instances at once?
instances = [ComposedMoranInstance.load_instance(name) for name in instanceNames]
totalRepsInACycle = sum([instance.totalSteps for instance in instances])
barSize = cyclesPerInstance*floor(totalRepsInACycle/callbackEach)
bar = ParallelBar(barSize)

# Go!
def run(sim: ComposedMoranInstance):
    for i in range(cyclesPerInstance):
        print(f"Executing {sim.instanceData.name} [{i+1}/{cyclesPerInstance}]")

        sim.do_cycle(saveEach=saveEach, iterationCallback=bar.tick, callbackEach=callbackEach)

        sim.instanceData.save_instance()

        print(f"Done {sim.instanceData.name} [{i+1}/{cyclesPerInstance}]")

    return 0

with Pool(threads) as pool:
    pool.map(run, instances)

bar.wait()