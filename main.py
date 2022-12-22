from city import City
from scheduler import Scheduler
from simulation import Simulation
import numpy as np
import pandas as pd
import sys
if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    # sys.stdout = sys.stderr = open('logfile', 'a')
    dati = pd.read_csv('data.csv')
    lbd = pd.read_csv('lambda.csv')
    shif_pars = pd.read_csv('shift.csv')
    
    '''---> costruzione della città'''
    matrix = pd.read_csv("matrice_torino.csv", sep=';', header=0, index_col=None).to_numpy()

    prova = City(np.array(matrix), dati)
    
    fail=10000
    repair=200
    schedules = Scheduler(dati, shif_pars, lbd, fail, repair)
    prova.build()

    '''--->setting of simulation'''
    duration = 3600*24*365 #1 year    
    sim = Simulation(schedules, duration, prova)
    sim.start()

    def energyPV(start,end,power):
        t = end-start 
        return int(0.8*t/3600*power)    #return Wh
        
    def totEnergyPv(df,power):
        total_consumption = 0
        for i in range(len(df)):
            total_consumption += energyPV(df.at[i,'SUNRISE'],df.at[i,'SUNSET'],df.at[i,'PV']*power)
        return total_consumption

    a,b = prova.totalConsumption()
    print('Total of energy = ',a/1000)
    print('total switch-on hours = ',b/3600)
    print('Total energy from photovoltaic panels = ',totEnergyPv(dati,200))

    
    
    