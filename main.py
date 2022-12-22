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
    
    fail=1000
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
        
    def totEnergyPv(df,power,battery):
        total_consumption = 0
        for i in range(len(df)):
            total_consumption += energyPV(df.at[i,'SUNRISE'],df.at[i,'SUNSET'],df.at[i,'PV']*power)
        if total_consumption > (battery*len(df)):
            return battery*len(df)
        else:
            return total_consumption

    a,b,c = prova.totalConsumption()
    print('Total energy consumption all lamps = ',a/1000,'kWh')
    print('Total hour on all lamps = ',b/3600,'hours')
    print('Total hours of single lamps = ',c/3600,'hours')
    nLampsPV=100
    battery=300
    powerPV=30
    print('Energy saved (one year) with PV panel, single lamp = ',totEnergyPv(dati,powerPV,battery)/1000,'kWh')
    print('Energy saved (one year) with PV panel,',nLampsPV,'lamps = ',nLampsPV*totEnergyPv(dati,powerPV,battery)/1000,'kWh')
    powerLed = 100
    totalLamps=2334
    x,y=prova.totalConsumptionNoSchedule(powerLed)
    print('Total energy consumption without scheduling (single lamp) = ',x/1000,'kWh')
    print('Total energy consumption without scheduling (all lamp) = ',x*totalLamps/1000,'kWh')
    print('Total hours without scheduling (single lamp) = ',y/3600,'hours')
    print('Total hours without scheduling (all lamp) = ',y*totalLamps/3600,'hours')

    
    
    