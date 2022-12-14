from lamp import *


class City:
    """ matrice sparsa dove alcuni nodi corrispondono a lampioni """

    def __init__(self):
        self.lampsCount = 0  # numero i lampioni
        self.lamps = []  # lista dei lampioni
        pass

    def addLamp(self, pos):
        """ aggiunge un lampione nella casella pos[0], pos[1]"""
        self.lamps.append(Lamp(self.lampsCount, pos))
        self.lampsCount += 1
        pass
