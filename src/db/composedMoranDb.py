from os import path, mkdir, listdir
from datetime import datetime
import json
import re

from env import Env

# Define file paths
dataFolder = Env.DATA_FOLDER.name
deterministicParamsFolder = path.join(dataFolder, Env.PARAMS_FOLDER.name)
cycleDataFolder = path.join(dataFolder, Env.CYCLE_DATA_FOLDER.name)
simInstancesFolder = path.join(dataFolder, Env.COMPOSED_INSTANCES_FOLDER.name)

class ComposedMoranParams:
    def __init__(self, paramsName, description, MList, wList, tList):
        self.name = paramsName
        self.description = description
        self.MList = MList
        self.wList = wList
        self.tList = tList
        self.simType = "composed"

    @staticmethod
    def load_params(name):
        filePath = path.join(deterministicParamsFolder, name)
        file = open(filePath)
        params = json.load(file)
        file.close()

        return ComposedMoranParams(
            params["name"],
            params["description"],
            params["MList"],
            params["wList"],
            params["tList"]
        )


class ComposedMoranInstanceData:
    def __init__(self, instanceName, paramsName, initialPopulation, currentPopulation, currentCycle):
        self.name = instanceName
        self.params = ComposedMoranParams.load_params(paramsName)
        self.initialPopulation = initialPopulation
        self.currentPopulation = currentPopulation
        self.currentCycle = currentCycle
        self.populationSize = sum(currentPopulation)

    @staticmethod
    def create_instance(paramsName, initialPopulation, instanceName=None):
        if instanceName is None:
            timestamp = int(round(datetime.now().timestamp()))
            instanceName = f"{paramsName}_{timestamp}"

        instanceData = ComposedMoranInstanceData(
            instanceName,
            paramsName,
            initialPopulation,
            initialPopulation,
            0
        )

        instanceData.save_instance()
        instanceDataFolder = path.join(cycleDataFolder, instanceName)
        mkdir(instanceDataFolder)

        return instanceData

    @staticmethod
    def load_instance(name):
        filePath = path.join(simInstancesFolder, name)
        file = open(filePath)
        params = json.load(file)
        file.close()

        return ComposedMoranInstanceData(
            params["name"],
            params["paramsName"],
            params["initialPopulation"],
            params["currentPopulation"],
            params["currentCycle"]
        )

    def save_instance(self):
        params = {
            "name": self.name,
            "paramsName": self.params.name,
            "initialPopulation": self.initialPopulation,
            "currentPopulation": self.currentPopulation,
            "currentCycle": self.currentCycle
        }

        filePath = path.join(simInstancesFolder, self.name)
        with open(filePath, "w") as file:
            json.dump(params, file)

    @staticmethod
    def list_instances(regex):
        fullFilelist = listdir(simInstancesFolder)

        return [filename for filename in fullFilelist if re.match(regex, filename)]


class CycleData:

    def __init__(self, instanceName, cycleNumber, initialPopulation, finalPopulation, bufferSize=100):
        # General attributes
        self.instanceName = instanceName
        self.cycleNumber = cycleNumber
        self.initialPopulation = initialPopulation
        self.finalPopulation = finalPopulation

        # Data saving attributes
        self.__iterations_file = None

        if bufferSize < 1:
            bufferSize = 1

        self.__bufferSize = bufferSize
        self.__stepBuffer = [None]*bufferSize
        self.__stepBuffer[0] = str(initialPopulation)
        self.__bufferIndex = 1

    @staticmethod
    def load_summarized_data(instanceName, cycleNumber):
        filePath = path.join(cycleDataFolder, instanceName, f"iterationBrief_{cycleNumber}")
        file = open(filePath)
        params = json.load(file)
        file.close()

        return CycleData(
            instanceName,
            cycleNumber,
            params["initialPopulation"],
            params["finalPopulation"]
        )
    
    @staticmethod
    def start_cycle(instanceName, cycleNumber, initialPopulation, bufferSize=100):
        cycleData = CycleData(instanceName, cycleNumber, initialPopulation, None, bufferSize)
        
        filePath = path.join(cycleDataFolder, instanceName, f"iterationDump_{cycleNumber}")
        if path.exists(filePath):
            raise Exception("Iterations file already exists!")

        cycleData.__iterations_file = open(filePath, "w")
        cycleData.__iterations_file.write("[\n")

        return cycleData
    
    def write_step(self, step):
        if self.__iterations_file is None:
            raise Exception("To write steps, please start a new cycle (start_cycle)")
        
        # If buffer is full, write it to memory and reset index
        if self.__bufferIndex == self.__bufferSize:
            accumulatedSteps = ",".join(self.__stepBuffer)        
            self.__iterations_file.write(f"{accumulatedSteps},\n")
            self.__bufferIndex = 0

        # Add step to buffer
        self.__stepBuffer[self.__bufferIndex] = str(step)
        self.__bufferIndex += 1

    def end_cycle(self):
        if self.__iterations_file is None:
            raise Exception("This cycle wasn't even started (start_cycle)")
        
        # Write final steps
        accumulatedSteps = ",".join(self.__stepBuffer[0:self.__bufferIndex]) 
        self.__iterations_file.write(f"{accumulatedSteps}\n]")
        self.__iterations_file.close()

        # Set final population
        self.finalPopulation = eval(self.__stepBuffer[self.__bufferIndex-1])

        self.__iterations_file = None

        self.__save_summarized_data()
    
    def __save_summarized_data(self):
        params = {
            "instanceName": self.instanceName,
            "cycleNumber": self.cycleNumber,
            "initialPopulation": self.initialPopulation,
            "finalPopulation": self.finalPopulation,
        }

        filePath = path.join(cycleDataFolder, self.instanceName, f"iterationBrief_{self.cycleNumber}")
        with open(filePath, "w") as file:
            json.dump(params, file)

    def load_cycle_data(self):
        filePath = path.join(cycleDataFolder, self.instanceName, f"iterationDump_{self.cycleNumber}")
        file = open(filePath)
        iterationsData = json.load(file)
        file.close()

        return iterationsData

