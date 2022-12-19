from city import City
from simulation import Simulation
import numpy as np

if __name__ == '__main__':
    ''' due fasi: prima la costruzione della città, poi la simulazione'''

    '''---> costruzione della città'''
    m =[[0,0,1,0,0,0,1,0,0,0],
        [0,0,1,0,0,0,1,0,0,0],
        [1,1,1,1,1,1,1,1,1,1],
        [0,0,1,0,0,0,1,0,0,0],
        [0,0,1,0,0,0,1,0,0,0],
        [1,1,1,1,1,1,1,1,1,1],
        [0,0,1,0,0,0,1,0,0,0],
        [0,0,1,0,0,0,1,0,0,0],
        [1,1,1,1,1,1,1,1,1,1],
        [0,0,1,0,0,0,1,0,0,0],]
    
    m2 = [[1,0,0],[1,0,0],[1,0,0]]

    prova=City(np.array(m))

    prova.build()

    print(prova.matrix[2][2].neigh)




    '''--->simulazione'''
    # duration = 10
    # sim = Simulation(duration, city)
    # sim.start()
