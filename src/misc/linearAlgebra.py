import numpy as np


def baseVector(dimension, direction):
    v = np.zeros(dimension)
    v[direction] = 1

    return v