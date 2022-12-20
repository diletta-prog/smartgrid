from city import City
from scheduler import Scheduler
from simulation import Simulation
import numpy as np
import pandas as pd

if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    dati = pd.read_csv('data.csv')
    lbd = pd.read_csv('lambda.csv')
    shif_pars = pd.read_csv('shift.csv')
    
    matrix = pd.read_csv("matrice_torino.csv", sep=';', header=0, index_col=None).to_numpy()

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

    prova = City(np.array(m), dati)
    fail=10
    repair=20
    schedules = Scheduler(dati, shif_pars, lbd, fail, repair)
    prova.build()

    # print(prova.matrix[2][2].neigh)
    '''--->simulazione'''
    duration = 100 #60*15   1 ora
    sim = Simulation(schedules, duration, prova)
    sim.start()
