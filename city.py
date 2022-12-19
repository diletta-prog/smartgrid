from itertools import product

from lamp import *
import numpy as np


class City:
    """ matrice sparsa dove alcuni nodi corrispondono a lampioni """

    def __init__(self, m):
        self.lampsCount = 0  # numero i lampioni
        self.matrixRaw = m == 1  # mi salvo la matrice grezza con 0 e 1
        self.matrix = np.empty(shape=np.shape(m), dtype=object)  # matrice di oggetti che saranno lampioni
        pass




    def build(self):
        """ istanzion tutti i lampioni """
        for x, y in product(range(self.matrixRaw.shape[0]), range(self.matrixRaw.shape[1])):
            if self.matrixRaw[x][y]: self.addLamp((x, y))
        """ per ogni lampione, mi salvo i vicini"""
        for lamp in self.matrix[self.matrix != None]:
            self.checkNeigh(lamp, np.where(self.matrix == lamp))




    def addLamp(self, pos):
        """creo la matrice di lampioni partendo da quella di 1 e 0"""
        newLamp = Lamp(self.lampsCount, pos)
        self.matrix[pos[0]][pos[1]] = newLamp  # inserisco oggetto lampione
        self.lampsCount += 1  # incremento numero lampioni





    def checkNeigh(self, lamp, pos):

        x = pos[0][0]
        y = pos[1][0]
        try:
            if x - 1 >= 0:
                lamp.addNeigh('up', self.matrix[x - 1][y].id)
        except:
            pass
        try:
            lamp.addNeigh('down', self.matrix[x + 1][y].id)
        except:
            pass
        try:
            if y - 1 >= 0:
                lamp.addNeigh('left', self.matrix[x][y - 1].id)
        except:
            pass
        try:
            lamp.addNeigh('right', self.matrix[x][y + 1].id)
        except:
            pass
        lamp.checkIntersection()
