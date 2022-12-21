from city import City
from scheduler import Scheduler
from simulation import Simulation
import numpy as np
import pandas as pd
import sys
if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    #
    # sys.stdout = sys.stderr = open('logfile', 'a')
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

    m3 =[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ]

    prova = City(np.array(m3), dati)
    
    fail=10000
    repair=200
    schedules = Scheduler(dati, shif_pars, lbd, fail, repair)
    prova.build()

    # print(prova.matrix[2][2].neigh)
    '''--->simulazione'''
    duration = 3600*24*360#  1 ora
    sim = Simulation(schedules, duration, prova)
    sim.start()

    def energyPV(start,end,power):
        t = end-start # start e end in secondi!!!!
        return int(0.8*t/3600*power)    # mi restituisce i WattORA
        
    def totEnergyPv(df,power):
        total_consumption = 0
        for i in range(len(df)):
            total_consumption += energyPV(df.at[i,'SUNRISE'],df.at[i,'SUNSET'],df.at[i,'PV']*power)
        return total_consumption

    a,b = prova.totalConsumption()
    print('Energia totale consumata = ',a/1000)
    print('Secondi totali accese = ',b/3600)
    print('PV = ',totEnergyPv(dati,200))

    
    
    