from itertools import product
from random import randint

from lamp import *
import numpy as np


class City:
    """ matrice sparsa dove alcuni nodi corrispondono a lampioni """

    def __init__(self, m, dati):
        self.lampsCount = 0  # numero i lampioni
        self.matrixRaw = m == 1  # mi salvo la matrice grezza con 0 e 1
        self.matrix = np.empty(shape=np.shape(m), dtype=object)  # matrice di oggetti che saranno lampioni
        self.dati = dati
        self.lampioni = []
        pass

    def build(self):
        """ istanzio tutti i lampioni """
        for x, y in product(range(self.matrixRaw.shape[0]), range(self.matrixRaw.shape[1])):
            if self.matrixRaw[x][y]: self.addLamp((x, y))
        """ per ogni lampione, mi salvo i vicini"""
        for lamp in self.matrix[self.matrix != None]:
            self.checkNeighs(lamp, np.where(self.matrix == lamp))

    def allLamps(self):
        return [lamp for lamp in self.matrix[self.matrix != None]]

    def addLamp(self, pos):
        self.matrix[pos[0]][pos[1]] = Lamp(self.lampsCount, pos)  # inserisco oggetto lampione
        self.lampioni.append(Lamp(self.lampsCount, pos).getID())
        self.lampsCount += 1  # incremento numero lampioni

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


    # def updateState(self, newBaseValue):
    #     """ aggiorniamo il valore base di tutti i lampioni, li resettiamo tutti al valore base !!! sbagliato"""
    #     for lamp in self.matrix[self.matrix != None]:
    #         lamp.setLevel(newBaseValue)


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



