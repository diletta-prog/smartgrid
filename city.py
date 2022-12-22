from itertools import product
from random import randint

from lamp import *
import numpy as np


class City:
    """ Scattered matrix where some nodes correspond to lampposts """

    def __init__(self, m, dati):
        self.lampsCount = 0  #number of lampposts
        self.matrixRaw = m == 1  # matrix raw with 0/1
        self.matrix = np.empty(shape=np.shape(m), dtype=object)  # matrix of lampposts
        self.dati = dati
        self.lampioni = []
        pass

    def build(self):
        """Inizialise lampposts """
        for x, y in product(range(self.matrixRaw.shape[0]), range(self.matrixRaw.shape[1])):
            if self.matrixRaw[x][y]: self.addLamp((x, y))
        """ Takes note of neighbours"""
        for lamp in self.matrix[self.matrix != None]:
            self.checkNeighs(lamp, np.where(self.matrix == lamp))

    def allLamps(self):
        return [lamp for lamp in self.matrix[self.matrix != None]]

    def addLamp(self, pos):
        self.matrix[pos[0]][pos[1]] = Lamp(self.lampsCount, pos)  # insert lamppost object
        self.lampioni.append(Lamp(self.lampsCount, pos).getID())
        self.lampsCount += 1  # count of lampposts + 1

    def checkNeighs(self, lamp, pos):
        x = pos[0][0]
        y = pos[1][0]
        try:
            if x - 1 >= 0 :
                lamp.addNeigh('up', self.matrix[x - 1][y], self.matrix[x - 1][y].id)
        except:
            pass
        try:
            lamp.addNeigh('down', self.matrix[x + 1][y],self.matrix[x + 1][y].id)
        except:
            pass
        try:
            if y - 1 >= 0:
                lamp.addNeigh('left', self.matrix[x][y - 1],self.matrix[x][y - 1].id)
        except:
            pass
        try:
            lamp.addNeigh('right', self.matrix[x][y + 1],self.matrix[x][y + 1].id)
        except:
            pass
        lamp.checkIntersection()



    def randomLamp(self):
        return self.searchLampById(randint(0, self.lampsCount - 1))


    def searchLampById(self, id):
        for lamp in self.matrix[self.matrix != None]:
            if lamp.id == id:
                return lamp

    def totalConsumption(self):
        energy = 0
        hour = 0
        single = 0
        for lamp in self.matrix[self.matrix != None]:
            single = lamp.getUtilization()
            energy += lamp.getPowerUtilization()
            hour += lamp.getUtilization()
        return energy, hour, single

    def totalConsumptionNoSchedule(self,powerLED):
        energy = 0
        time = 0
        for i in range(len(self.dati)):
            energy +=  (int(self.dati.at[i,'SUNSET']) - int(self.dati.at[i,'SUNRISE']))/3600 * powerLED
            time += (int(self.dati.at[i,'SUNSET']) - int(self.dati.at[i,'SUNRISE']))
        return energy,time



