class Lamp:
    """ lampione, con diversi attributi:
    --> id
    -->posizione nella matrice
    -->livello di intensità luminosa]
    --> stato [funzionante/ non funzionante]
    --> lista dei vicini
    """

    def __init__(self, id, pos, lev=0, stato='on'):
        self.id = id
        self.pos = pos
        self.lev = lev
        self.state = stato
        self.neigh = []

    def setLevel(self, newLevel):
        self.lev = newLevel

    def setState(self, newState):
        self.state = newState

    def addNeigh(self, newNeigh):
        self.neigh.append(newNeigh)
