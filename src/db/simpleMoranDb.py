from os import path, mkdir, listdir
from datetime import datetime
import json
import re

from env import Env

# Define file paths
dataFolder = Env.DATA_FOLDER.name
deterministicParamsFolder = path.join(dataFolder, Env.PARAMS_FOLDER.name)
executionDataFolder = path.join(dataFolder, Env.EXECUTION_DATA_FOLDER.name)
simInstancesFolder = path.join(dataFolder, Env.SIMPLE_INSTANCES_FOLDER.name)

class SimpleMoranParams:
    def __init__(self, paramsName, description, M, w):
        self.name = paramsName
        self.description = description
        self.M = M
        self.w = w
        self.simType = "simple"

    @staticmethod
    def load_params(name):
        filePath = path.join(deterministicParamsFolder, name)
        file = open(filePath)
        params = json.load(file)
        file.close()

        return SimpleMoranParams(
            params["name"],
            params["description"],
            params["M"],
            params["w"]
        )


class SimpleMoranInstanceData:
    def __init__(self, instanceName, paramsName, initialPopulation, fixatedIndex, lastStep):
        self.name = instanceName
        self.params = SimpleMoranParams.load_params(paramsName)
        self.initialPopulation = initialPopulation
        self.fixatedIndex = fixatedIndex
        self.lastStep = lastStep
        self.populationSize = sum(initialPopulation)

    @staticmethod
    def create_instance(paramsName, initialPopulation, instanceName=None):
        if instanceName is None:
            timestamp = int(round(datetime.now().timestamp()))
            instanceName = f"{paramsName}_{timestamp}"

        instanceData = SimpleMoranInstanceData(
            instanceName,
            paramsName,
            initialPopulation,
            None,
            None
        )

        instanceData.save_instance()
        instanceDataFolder = path.join(executionDataFolder, instanceName)
        mkdir(instanceDataFolder)

        return instanceData

    @staticmethod
    def load_instance(name):
        filePath = path.join(simInstancesFolder, name)
        file = open(filePath)
        params = json.load(file)
        file.close()

        return SimpleMoranInstanceData(
            params["name"],
            params["paramsName"],
            params["initialPopulation"],
            params["fixatedIndex"],
            params["lastStep"]
        )

    def save_instance(self):
        params = {
            "name": self.name,
            "paramsName": self.params.name,
            "initialPopulation": self.initialPopulation,
            "fixatedIndex": self.fixatedIndex,
            "lastStep": self.lastStep
        }

        filePath = path.join(simInstancesFolder, self.name)
        with open(filePath, "w") as file:
            json.dump(params, file)

    @staticmethod
    def list_instances(regex):
        fullFilelist = listdir(simInstancesFolder)

        return [filename for filename in fullFilelist if re.match(regex, filename)]

class IterationData:

    def __init__(self, instanceName, initialPopulation, lastStep, fixatedIndex, bufferSize=1000):
        # General attributes
        self.instanceName = instanceName
        self.lastStep = lastStep
        self.initialPopulation = initialPopulation
        self.fixatedIndex = fixatedIndex

        # Data saving attributes
        self.__iterations_file = None

        if bufferSize < 1:
            bufferSize = 1

        self.__bufferSize = bufferSize
        self.__stepBuffer = [None]*bufferSize
        self.__stepBuffer[0] = str(initialPopulation)
        self.__bufferIndex = 1

    @staticmethod
    def load_summarized_data(instanceName):
        filePath = path.join(executionDataFolder, instanceName, f"iterationBrief")
        file = open(filePath)
        params = json.load(file)
        file.close()

        return IterationData(
            instanceName,
            params["initialPopulation"],
            params["lastStep"],
            params["fixatedIndex"]
        )
    
    @staticmethod
    def start_iterations(instanceName, initialPopulation, bufferSize=1000):
        iterationData = IterationData(instanceName, initialPopulation, None, None, bufferSize)
        
        filePath = path.join(executionDataFolder, instanceName, f"iterationDump")
        if path.exists(filePath):
            raise Exception("Iterations file already exists!")

        iterationData.__iterations_file = open(filePath, "w")
        iterationData.__iterations_file.write("[\n")

        return iterationData
    
    def write_step(self, step):
        if self.__iterations_file is None:
            raise Exception("To write steps, please start a new iteration (start_iterations)")
        
        # If buffer is full, write it to memory and reset index
        if self.__bufferIndex == self.__bufferSize:
            accumulatedSteps = ",".join(self.__stepBuffer)        
            self.__iterations_file.write(f"{accumulatedSteps},\n")
            self.__bufferIndex = 0

        # Add step to buffer
        self.__stepBuffer[self.__bufferIndex] = str(step)
        self.__bufferIndex += 1

    def end_iterations(self, lastStep, fixatedIndex):
        if self.__iterations_file is None:
            raise Exception("These iterations weren't even started (start_iterations)")
        
        # Write final steps
        accumulatedSteps = ",".join(self.__stepBuffer[0:self.__bufferIndex]) 
        self.__iterations_file.write(f"{accumulatedSteps}\n]")
        self.__iterations_file.close()

        # Set fixation data
        self.fixatedIndex = fixatedIndex
        self.lastStep = lastStep

        self.__iterations_file = None

        self.__save_summarized_data()
    
    def __save_summarized_data(self):
        params = {
            "instanceName": self.instanceName,
            "initialPopulation": self.initialPopulation,
            "lastStep": self.lastStep,
            "fixatedIndex": self.fixatedIndex,
        }

        filePath = path.join(executionDataFolder, self.instanceName, f"iterationBrief")
        with open(filePath, "w") as file:
            json.dump(params, file)

    def load_iteration_data(self):
        filePath = path.join(executionDataFolder, self.instanceName, f"iterationDump")
        file = open(filePath)
        iterationsData = json.load(file)
        file.close()

        return iterationsData
    