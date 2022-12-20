from random import choice

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

    def __init__(self, id, pos, power_max=100, lev=0, stato='on'):
        self.id = id  # id
        self.pos = pos  # posizione nella matrice
        self.lev = lev  # livello intensità
        self.state = stato  # stato (off, on, fail)
        self.power_max = power_max  # potenza massima lampadina
        self.neigh = {}  # ID lampioni vicini
        self.busy = 0
        self.utilization = 0    # tempo di utilizzo
        self.power_utilization = 0  # wattOra consumati
        self.time_on = 0    # orario di accensione


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
        self.busy = busy

    def setLevel(self, newLevel):
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
            #print(list(filter(lambda x: x != opposite(exclude), self.neigh.keys())))
            return choice(list(filter(lambda x: x != opposite(exclude), self.neigh.keys())))

    def consumption(self, clock):
        self.utilization += (clock-self.time_on)
        self.power_utilization += (clock-self.time_on)*(self.lev/100*self.power_max)