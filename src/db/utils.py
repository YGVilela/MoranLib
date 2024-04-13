# Load environment variables
import json
from os import path

from env import Env
from src.db.composedMoranDbDb import ComposedMoranParams, ComposedMoranInstanceData
from src.db.simpleMoranDb import SimpleMoranParams, SimpleMoranInstanceData


# Define file paths
dataFolder = Env.DATA_FOLDER.name
deterministicParamsFolder = path.join(dataFolder, Env.PARAMS_FOLDER.name)

def load_params(name):
    filePath = path.join(deterministicParamsFolder, name)
    file = open(filePath)
    params = json.load(file)
    file.close()

    if params["type"] == "simple":
        return SimpleMoranParams(
            params["name"],
            params["description"],
            params["M"],
            params["w"]
        )
    elif params["type"] == "composed":
        return ComposedMoranParams(
            params["name"],
            params["description"],
            params["MList"],
            params["wList"],
            params["tList"]
        )
    
def get_instance_data_class(simType):
    if simType == "simple":
        return SimpleMoranInstanceData
    elif simType == "composed":
        return ComposedMoranInstanceData