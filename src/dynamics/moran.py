import numpy as np
from random import random
from math import floor

from src.misc.linearAlgebra import baseVector


class MoranProcess:
    def __init__(self, M, w, N):
        self.M = np.array(M)
        self.w = np.array(w)
        self.N = N

        self.d = len(M)
        self.basis = [baseVector(self.d, i) for i in range(self.d)]

        # Fitness of type i is defined as 1 - w_i + w_i*(M.(x - e_i)/(N-1))
        # We define the following to improve performance
        self.modifiedM = (self.w*self.M.transpose()).transpose()/(self.N-1)
        self.additiveTerm = np.ones(self.d) - self.w - [self.modifiedM[i, i] for i in range(self.d)]
    
    def transitionProb(self, X):
        # Evaluate fitness
        fitness = np.dot(self.modifiedM, X) + self.additiveTerm

        # Evaluate total fitness
        populationFitness = fitness*X
        totalFitness = sum(populationFitness)

        # Compute probabilities
        birthProb = populationFitness/totalFitness
        deathProb = X/self.N
    
        return np.array([
            [
                birthProb[i]*deathProb[j] 
                for j in range(self.d)
            ]
            for i in range(self.d)
        ])
    
    def iterate(self, X):
        transitionArray = np.cumsum(self.transitionProb(X).flatten())
        randNumber = random()

        # Gets index of first True value
        selectedIndex = np.argmax(transitionArray >= randNumber)

        selectedBirth = floor(selectedIndex/self.d)
        selectedDeath = selectedIndex%self.d

        # Update variables
        return X + self.basis[selectedBirth] - self.basis[selectedDeath]
