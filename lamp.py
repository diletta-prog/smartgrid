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

    def __init__(self, id, pos, lev=0, stato='on'):
        self.id = id  # id
        self.pos = pos  # posizione nella matrice
        self.lev = lev  # livello intensità
        self.state = stato  # stato
        self.neigh = {}  # ID lampioni vicini

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
            print(list(filter(lambda x: x != opposite(exclude), self.neigh.keys())))
            return choice(list(filter(lambda x: x != opposite(exclude), self.neigh.keys())))
