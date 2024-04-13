class Variable:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class Env:
    DATA_FOLDER= Variable(
        "samples",
        "Main data folder."
    )

    PARAMS_FOLDER= Variable(
        "params",
        "Folder with general parameters for the Moran processes."
    )
    
    SIMPLE_INSTANCES_FOLDER= Variable(
        "simpleSimInstances",
        "Folder with simulation state of simple Moran processes."
    )
    
    COMPOSED_INSTANCES_FOLDER= Variable(
        "composedSimInstances",
        "Folder with simulation state of composed Moran processes."
    )
    
    CYCLE_DATA_FOLDER= Variable(
        "cycleData",
        "Folder with simulation data of simple Moran processes."
    )
    
    STATS_FOLDER= Variable(
        "stats",
        "Folder with simulation data of composed Moran processes."
    )
    
    EXECUTION_DATA_FOLDER= Variable(
        "executionData",
        "Folder with simulation stats."
    )

    SUBFOLDERS = [
        PARAMS_FOLDER,
        SIMPLE_INSTANCES_FOLDER,
        COMPOSED_INSTANCES_FOLDER,
        CYCLE_DATA_FOLDER,
        STATS_FOLDER,
        EXECUTION_DATA_FOLDER
    ]