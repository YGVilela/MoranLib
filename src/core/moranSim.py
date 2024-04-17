from math import ceil
from numpy import array, cumsum

from src.db.composedMoranDb import CycleData, ComposedMoranInstanceData
from src.db.simpleMoranDb import IterationData, SimpleMoranInstanceData
from src.dynamics.moran import MoranProcess

class SimpleMoranInstance:

    def __init__(self, instanceData: SimpleMoranInstanceData):
        self.instanceData = instanceData

        params = instanceData.params
        self.process = MoranProcess(params.M, params.w, instanceData.populationSize)

    @staticmethod
    def load_instance(instanceName):
        instanceData = SimpleMoranInstanceData.load_instance(instanceName)

        return SimpleMoranInstance(instanceData)

    def execute(self, maxIterations=1E6, bufferSize=1000):
        if self.instanceData.lastStep != None:
            print(f"Executing {self.instanceData.name} already executed.")

            return self.instanceData.lastStep, self.instanceData.fixatedIndex

        X = array(self.instanceData.initialPopulation)

        executionData = IterationData.start_iterations(
            self.instanceData.name,
            X.tolist(),
            bufferSize
        )

        print(f"Executing {self.instanceData.name} until fixation.")
        steps = 0
        fixatedIndex = None
        while steps < maxIterations:
            X = self.process.iterate(X)

            # Save population
            executionData.write_step(X.tolist())
            steps += 1

            # Check if reached fixation
            if len([x for x in X if x > 0]) == 1:
                fixatedIndex = [
                    index + 1
                    for index in range(len(X.tolist()))
                    if X[index] > 0
                ][0]

                break

        self.instanceData.lastStep = steps
        self.instanceData.fixatedIndex = fixatedIndex

        executionData.end_iterations(steps, fixatedIndex)
        
        return steps, fixatedIndex


class ComposedMoranInstance:

    def __init__(self, instanceData: ComposedMoranInstanceData):
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
        instanceData = ComposedMoranInstanceData.load_instance(instanceName)

        return ComposedMoranInstance(instanceData)

    def do_cycle(self, saveEach=50000, iterationCallback=None, callbackEach=1000, bufferSize=100):
        X = array(self.instanceData.currentPopulation)

        cycleData = CycleData.start_cycle(
            self.instanceData.name,
            self.instanceData.currentCycle,
            X.tolist(),
            bufferSize
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
        if not (saveEach >= 1 and (self.totalSteps - 1) % saveEach != 0):
            cycleData.write_step(X.tolist())

        cycleData.end_cycle()

        self.instanceData.currentCycle += 1
        self.instanceData.currentPopulation = X.tolist()
