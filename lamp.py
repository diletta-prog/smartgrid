from random import choice
import numpy as np

from directions import opposite


class Lamp:
    """ 
    lampione, con diversi attributi:
    --> id
    --> posizione nella matrice
    --> livello di intensità luminosa
    --> stato [funzionante / non funzionante]
    --> lista dei lampioni vicini
    
    """

    def __init__(self, id, pos, power_max=100, lev=0, stato='ok'):
        self.id = id  # id
        self.pos = pos  # position in matrix
        self.lev = lev  # level of intensity
        self.state = stato  # state: ok, fail
        self.power_max = power_max  # max power of lamp
        self.neigh = {}  # ID neighbours
        self.busy = 0
        self.utilization = 0    # time of utilization
        self.power_utilization = 0  # Wh consumed
        self.time_on = 0    # time in wich we turned on


    def clearLamps(self):
        self.lev=0
        self.busy=0
        self.time_on=0


    def setTimeOn(self,clock):
        self.time_on = clock

    def getPowerUtilization(self):
        return self.power_utilization

    def getUtilization(self):
        return self.utilization

    def getPos(self):
        return self.pos[0], self.pos[1]

    def getLevel(self):
        return self.lev

    def getState(self):
        return self.state

    def getID(self):
        return self.id

    def getNeigh(self, pos):
        return self.neigh[pos]

    def setBusy(self,busy):
        if busy == 1: 
            self.busy +=1
        elif busy == 0: 
            if (self.busy == 0):
                pass
            else:
                self.busy -=1
        elif busy == -1:
            self.busy = 0
        
    def getCambio(self):
        return self.cambi

    def setLevel(self, newLevel, clock):
        if self.lev != 0:
            self.consumption(clock)
        self.setTimeOn(clock)
        self.lev = newLevel

    def setState(self, newState):
        self.state = newState
        if newState == 'off': self.setLevel(0)

    def addNeigh(self, pos, newNeigh, id):
        self.neigh[pos] = newNeigh

    def checkIntersection(self):
        pass

    def randomNeigh(self, exclude=None):
        if exclude is None:
            return choice(list(self.neigh.keys()))
        else:
            return choice(list(filter(lambda x: x != opposite(exclude), self.neigh.keys())))

    def consumption(self, clock):
        self.utilization += (clock-self.time_on)
        self.power_utilization += (clock-self.time_on)/3600*(self.lev/100*self.power_max)


    def checkNeighState(self):
        fault = False
        for item in self.neigh.values():
            if item.getState() == 'fail':
                fault = True
        return fault