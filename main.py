from city import City
from simulation import Simulation

if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    '''---> costruzione della città'''
    city = City()



    '''--->simulazione'''
    duration = 10
    sim = Simulation(duration, city)
    sim.start()
