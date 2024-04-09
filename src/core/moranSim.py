from math import ceil
from numpy import array, cumsum

from src.db.moranDb import CycleData, InstanceData
from src.dynamics.moran import MoranProcess

class ComposedMoranInstance:

    def __init__(self, instanceData: InstanceData):
        self.instanceData = instanceData

        # Create one Moran process for each phase
        params = instanceData.params
        self.processes = [
            MoranProcess(params.MList[i], params.wList[i], instanceData.populationSize)
            for i in range(len(params.tList))
        ]

        # Init derived consts
        self.lastStepOfPhase = cumsum([
            ceil(timeOnPhase*instanceData.populationSize)
            for timeOnPhase in params.tList
        ])
        self.totalSteps = self.lastStepOfPhase[-1]

    @staticmethod
    def load_instance(instanceName):
        instanceData = InstanceData.load_instance(instanceName)

        return ComposedMoranInstance(instanceData)

    def do_cycle(self, saveEach=50000, iterationCallback=None, callbackEach=1000):
        X = array(self.instanceData.currentPopulation)

        cycleData = CycleData.start_cycle(
            self.instanceData.name,
            self.instanceData.currentCycle,
            X.tolist()
        )

        print(f"Executing {self.totalSteps} steps")
        currPhase = 0
        currProcess = self.processes[currPhase]
        for currStep in range(self.totalSteps):
            X = currProcess.iterate(X)

            # Save population
            if saveEach >= 1 and currStep % saveEach == 0:
                cycleData.write_step(X.tolist())

            # Execute callback
            if iterationCallback is not None and currStep % callbackEach == 0:
                iterationCallback()

            # Update currProcess
            if currStep == self.lastStepOfPhase[currPhase]:
                currPhase += 1
                currProcess = self.processes[currPhase]

        # If the last step was not written, write it
        if not (saveEach >= 1 and (self.totalSteps - 1) % saveEach == 0):
            cycleData.write_step(X.tolist())

        cycleData.end_cycle()

        self.instanceData.currentCycle += 1
        self.instanceData.currentPopulation = X.tolist()
