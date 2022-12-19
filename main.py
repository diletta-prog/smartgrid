from city import City
from simulation import Simulation
import numpy as np
import pandas as pd

if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    dati = pd.read_csv('data.csv')
    lbd = pd.read_csv('lambda.csv')

    '''---> costruzione della città'''
    m = [[0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [0, 0, 1, 0, 0, 0, 1, 0, 0, 0], ]

    m2 = [[1, 0, 0], [1, 0, 0], [1, 0, 0]]

    prova = City(np.array(m),dati)

    prova.build()

    # print(prova.matrix[2][2].neigh)
    '''--->simulazione'''
    duration = 100
    sim = Simulation(duration, prova, lbd)
    sim.start()
