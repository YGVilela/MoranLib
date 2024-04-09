"""
This script executes multiple Moran process simulations in parallel.

Usage:
    python3 resume_instance.py [-r INSTANCE_REGEX] [-n CYCLES_PER_INSTANCE] [-s SAVE_EACH] [-c CALLBACK_EACH] [-t THREADS]

Arguments:
    -r INSTANCE_REGEX, --instanceRegex INSTANCE_REGEX
        Regular expression to filter the simulations to be executed. Default is '.*'.

    -n CYCLES_PER_INSTANCE, --cyclesPerInstance CYCLES_PER_INSTANCE
        Number of cycles to be executed for each instance. Default is 1.

    -s SAVE_EACH, --saveEach SAVE_EACH
        Number of steps to be executed between each save. Default is 50000.

    -c CALLBACK_EACH, --callbackEach CALLBACK_EACH
        Number of steps to be executed between each progress bar tick. Default is 1000.

    -t THREADS, --threads THREADS
        Number of threads to be used in the execution. Default is 3.

Example:
    python3 resume_instance.py -r "stableRoutine_*|.*_stableRoutine_*" -n 2
    python3 resume_instance.py -r "unstableRoutine_*|.*_unstableRoutine_*" -n 2

Description:
    This script executes multiple Moran process simulations in parallel with specified parameters.
    It supports the following options:
    - Filtering simulation instances using a regular expression.
    - Specifying the number of cycles to be executed for each instance.
    - Setting the frequency of saving data and updating the progress bar.
    - Configuring the number of threads for parallel execution.

    The script performs the following steps:
    1. Parses command-line arguments to extract parameters.
    2. Loads simulation instances based on the specified regular expression.
    3. Prints information about the simulations to be executed.
    4. Initializes a progress bar to track simulation progress.
    5. Executes simulations in parallel using multiprocessing.
    6. Waits for all simulations to finish before exiting.
"""


import argparse
from src.misc.bars import CountdownBar, ParallelBar
from src.core.moranSim import ComposedMoranInstance
from src.db.moranDb import InstanceData
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
instanceNames = InstanceData.list_instances(instanceRegex)

# Safety check
print(f"Executing {len(instanceNames)} simulations {cyclesPerInstance} times. Is that correct?")
CountdownBar(5).start()

# Init instances and progress bar
# TODO: How can we change to avoid loading all instances at once?
instances = [ComposedMoranInstance.load_instance(name) for name in instanceNames]
totalReps = sum([instance.totalSteps for instance in instances])
barSize = cyclesPerInstance*floor(totalReps/callbackEach)
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