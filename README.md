# MoranLib

Project to simulate [Moran processes](https://en.wikipedia.org/wiki/Moran_process) and Moran routines, currently being developed by [Yuri Garcia Vilela](http://lattes.cnpq.br/7173465337985484).

## Environment Preparation

- Clone the repository

- [Install python](https://www.python.org/downloads/) (tested on version 3.9.12)

- Install the necessary python libraries (listed on _requirements.txt_)

## Setup

- Edit the _env.py_ file as needed to change the desired folder structure.

- Run _python3 setup.py_ to create the necessary folder structure.

## Simulation Parameters

The parameters for a simulation must be stored on `{DATA_FOLDER}/{PARAMS_FOLDER}` as configured on the _env.py_ file.

### Simple Moran Process

To simulate a simple Moran Process, you need to define its payment matrix "M" and selection coefficients "w". The parameter file has the following strucure:

```ts
{
    "name": string, // Name of the simulation.
    "description": string, // Short description of the simulated process.
    "type": "simple", // Simulation type.
    "M": float[][], // Payment matrix for the process.
    "w": float[] // Selection coefficients for the process.
}
```

#### Sample params:

```json
{
    "name": "prisonersDilemma",
    "description": "Two players interact in a repeated prisoner's dilemma game where mutual cooperation yields a payoff of 7 (R), mutual defection yields a payoff of 5 (P), temptation to defect yields a payoff of 10 (T) when the opponent cooperates, and the sucker's payoff is 0 (S) when the opponent defects. Population given as (#cooperators, #defectors).",
    "type": "simple",
    "M": [
        [7, 0],
        [10, 5]
    ],
    "w": [1, 1]
}

```

### Composed Moran Process

To simulate a composed Moran Process, you need to define its payment matrix "M" and selection coefficients "w" for phase, as well as the duration of said phases. The parameter file has the following strucure:

```ts
{
    "name": string, // Name of the simulation.
    "description": string, // Short description of the simulated process.
    "type": "composed", // Simulation type.
    "MList": float[][][], // Payment matrices for each phase of the process.
    "wList": float[][], // Selection coefficients for each phase of the process.
    "tList": float[] // Deterministic time for each phase of the process. The number steps on phase i for a simulation with populationSize individuals is given by tList[i]*poplationSize.
}
```

#### Sample params:

```json
{
    "name": "stableRoutine",
    "description": "Stable cyclic treatment routine designed with replicator dynamics for the initial composition x = (0.3, 0.2, 0.5).",
    "type": "composed",
    "MList": [
        [
            [2.0, 2.8, 2.8],
            [1.8, 1.8, 2.1],
            [1.8, 2.1, 1.8]
        ],
        [
            [2.0, 2.8, 2.8],
            [1.8, 1.8, 2.1],
            [1.8, 2.1, 1.8]
        ],
        [
            [2.0, 2.8, 2.8],
            [1.8, 1.8, 2.1],
            [1.8, 2.1, 1.8]
        ]
    ],
    "wList": [
        [0.1, 0.1, 0.1],
        [0.0, 0.1, 0.0],
        [0.0, 0.0, 0.1]
    ],
    "tList": [40, 20.4101, 21.9782]
}


```

## Scripts

### Creating new simulations

To create new simulations use the _new\_instance.py_ or the _create\_batch.py_ script with the command line:

#### Creating simulations with the same parameters

The _new\_instance.py_ script creates new instances of Moran simulations, all with the same parameters. It has the following usage:

```sh
python3 new_instances.py paramsName initialPopulation [-n SIM_COUNT] [-p NAME_PREFIX]
```

Its arguments are:

- paramsName: Name of the Moran parameters file to be used.
- initialPopulation: Initial population distribution for the simulations.
- -n, --simCount: Number of simulations to be created. Default is 1.
- -p, --namePrefix: Prefix to be used on the simulation's names. Default is an empty string.

#### Example usage:

```sh
python3 new_instances.py prisonersDilemma "(100, 100)" -n 10 -p "samplePD"
```
```sh
python3 new_instances.py stableRoutine "(300, 200, 500)" -n 10 -p "sampleStable"
```

#### Creating simulations with different parameters

The _create\_batch.py_ script creates new instances of Moran simulations with different parameters. It has the following usage:

```sh
python3 new_instances.py batchParamsFile.json
```

The _batchParamsFile.json_ must contain an array with items describing the instances to be created in for the [_new\_instances.py_](#creating-simulations-with-the-same-parameters) script.

#### Example json:

```json
[
    {
        "paramsName": "stableRoutine",
        "initialPopulation": [200, 300, 500],
        "simCount": 10,
        "namePrefix": "stableRep_1k"
    },
    {
        "paramsName": "lvRoutine",
        "initialPopulation": [167, 167, 666],
        "simCount": 10,
        "namePrefix": "stableLv_1k"
    },
    {
        "paramsName": "rockPaperScissors",
        "initialPopulation": [100, 100, 100],
        "simCount": 10,
        "namePrefix": "balancedRPS_300"
    }
]
```

### Executing the simulations

To execute the created simulations use the _execute\_simple\_moran.py_ script for [Simple Moran Processes](#simple-moran-process) or the resume\_composed\_moran.py_ script for [Composed Moran Processes](#composed-moran-process).

#### Executing Simple Moran Processes

The _execute\_simple\_moran.py_ script executes simple Moran simulations until fixation. It has the following usage:

```sh
python3 execute_simple_moran.py [-r INSTANCE_REGEX] [-t THREADS] [-m MAX_ITERATIONS]
```

and its arguments are:

- -r, --instanceRegex: Regular expression to filter the simulations that should be executed. Default is '.*'.
- -t, --threads: Number of threads to be used in the execution. Default is 3.
- -m, --maxIterations: Maximum number of iterations to perform for each simmulations. Default is 1,000,000.

#### Executing Composed Moran Processes

The _resume\_composed\_moran.py_ script resumes the execution of composed Moran simulations. It has the following usage:

```sh
python3 resume_composed_moran.py [-r INSTANCE_REGEX] [-n CYCLES_PER_INSTANCE] (-s SAVE_EACH | --saveTotal SAVE_TOTAL) [-c CALLBACK_EACH] [-t THREADS]
```

and its arguments are:

- -r, --instanceRegex: Regular expression to filter the simulations that should be executed. Default is '.*'.
- -n, --cyclesPerInstance: Number of cycles to be executed for each instance. Default is 1.
- -s, --saveEach: Number of steps to be executed between each save. Default is 50000.
- --saveTotal: Number of steps to be saved on each cycle. By default is derived from saveEach.
- -c, --callbackEach: Number of steps to be executed between each progress bar tick. Default is 1000.
- -t, --threads: Number of threads to be used in the execution. Default is 3.


#### Example usage:

```sh
python3 execute_simple_moran.py -r "samplePD*" -m 1000
```

```sh
python3 resume_composed_moran.py -r "sampleStable*" -n 2
```

### Getting simulation stats

To the get the stats for the executed simulations use the _get\_fixation\_stats.py_  or _plot\_simple\_evolution.py_ script for [Simple Moran Processes](#simple-moran-process) or the _get\_cycle\_stats.py_ script for [Composed Moran Processes](#composed-moran-process)

#### Getting the fixation stats

The _get\_fixation\_stats.py_ script generates fixation statistics for simple Moran simulations. It has the following usage:

```sh
python3 get_fixation_stats.py [-r INSTANCE_REGEX] [-f FOLDER]
```

and its arguments are:

- -r, --instanceRegex: Regular expression to filter the simulations that should be analysed. Default is '.*'.
- -f, --folder: Main folder to save the stats. Default is the one set in env.

#### Ploting simple Moran evolution

The _plot\_simple\_evolution.py_ script plots the mean evolution of several simple Moran instances with error bars. It has the following usage:

```sh
python3 plot_simple_evolution.py [-f FOLDER] [-s SAMPLESIZE] [-m MAXSTEP] (-j JSONARRAY | -l LIST | -r INSTANCEREGEX)
```

and its arguments are:

- -f FOLDER, --folder FOLDER: Main folder to save the stats. Default is the one set in env.
- -s SAMPLESIZE, --sampleSize SAMPLESIZE: Number of points to consider on each simulation. Default is 200.
- -m MAXSTEP, --maxStep MAXSTEP: Maximum step to be considered on the simulations. Default is 100000.
- -j JSONARRAY, --jsonArray JSONARRAY: JSON file containing an array with the names of the instances to be considered.
- -l LIST, --list LIST:  Names of the instances to be considered.
- -r INSTANCEREGEX, --instanceRegex INSTANCEREGEX: Regular expression to filter the simulations that should be analysed.

#### Getting cycle stats

The _get\_cycle\_stats.py_ script generates cycle statistics for composed Moran simulations. It has the following usage:

```sh
python3 get_cycle_stats.py [-r INSTANCE_REGEX] [-f FOLDER] [-d DELTA]
```

and its arguments are:

- -r, --instanceRegex: Regular expression to filter the simulations that should be analysed. Default is '.*'.
- -f, --folder: Main folder to save the stats. Default is the one set in env.
- -d, --delta: Length of the histograms intervals. Default is 0.02.

#### Example usage:

```sh
python3 get_fixation_stats.py -r "samplePD*"
```

```sh
python3 plot_simple_evolution.py -r "samplePD*" -m 500 -s 200
```

```sh
python3 get_cycle_stats.py -r "sampleStable*"
```