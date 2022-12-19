from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd
import pandas as pd

class Simulation:

    def __init__(self, duration, city, arrival_parameters=25, fail_parameter=1 / 500, shift_parameter=0.5, seed=0):
        self.duration = duration
        self.clock = 0
        self.seed = seed
        self.city = city
        self.fes = PriorityQueue()  # nella mia fes posso avere due tipi di eventi : arrivo di una macchina o un fail
        # del lampione
        self.arrival_parameters = arrival_parameters
        self.fail_parameter = fail_parameter
        self.base_value = 0
        self.shift_parameter = shift_parameter
        rd.seed(seed)







    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """
        lamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((0, self.arrival, (lamp, choice(list(lamp.neigh.keys())), randint(3, 10))))  # primo elemento

        while self.clock < self.duration:
            (self.clock, event, attr) = self.fes.get()
            event(attr)






    def shift(self, attributes):
        lamp, direction, ttl = attributes
        if ttl > 0:  # controllo se la macchina ha ancora time to live
            nextLamp = lamp.neigh[direction]
            nextLamp.setLevel(1.2 * self.base_value)
            try:  # next shift
                self.fes.put(
                    (self.clock + expovariate(1.0 / self.shift_parameter), self.shift, (
                        nextLamp, choice(list(filter(lambda x: x != self.opposite(direction), nextLamp.neigh.keys()))),
                        ttl - 1)))
            except:
                pass





    def arrival(self, attributes):

        """--->setto la luminosità di tutti i lampioni intorno"""
        lamp, direction, ttl = attributes
        lamp.setLevel(1.2 * self.base_value)
        for neigh in lamp.neigh.values():
            neigh.setLevel(1.2 * self.base_value)

        """--->scheulo il prossimo shift"""
        nextLamp = lamp.neigh[direction]
        self.fes.put((self.clock + expovariate(1.0 / self.shift_parameter), self.shift, (
            nextLamp, choice(list(filter(lambda x: x != self.opposite(direction), nextLamp.neigh.keys()))),
            ttl - 1)))

        """--> schedulo il next arrival"""
        nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        for _, el in self.arrival_parameters.iterrows():
            if self.clock < el['range']: 
                arrival_parameter = el['lambda']
                break
        self.fes.put((self.clock + expovariate(arrival_parameter), self.arrival,
                      (nextLamp, choice(list(nextLamp.neigh.keys())),
                       randint(3, 10))))







    def failure(self, **kwargs):
        """cosa facciamo in caso di una failure del lampione in posizione pos
        --> aumento l'intensità dei vicini


    dipende dal verso della strada


        --> schedulo il next fail """
        self.fes.put((self.clock + expovariate(1.0 / self.fail_parameter), "failure", randint(0, self.city.lampsCount)))

    def dailyUpdate(self):
        """ aggiorniamo il valore  base value"""
        if self.dati['meteo'] == 'sole':
            self.base_value = 50
        if self.dati['meteo'] == 'pioggia temporale ':
            self.base_value = 60
        if self.dati['meteo'] == 'pioggia neve ':
            self.base_value = 70
        if self.dati['meteo'] == 'pioggia nebbia ':
            self.base_value = 80
        if self.dati['meteo'] == 'pioggia ':
            self.base_value = 85
        if self.dati['meteo'] == 'neve nebbia ':
            self.base_value = 90
        if self.dati['meteo'] == 'nebbia ':
            self.base_value = 95
        self.city.updateState()

    def opposite(self, dir):
        if dir == 'left': return 'right'
        if dir == 'rigth': return 'left'
        if dir == 'up': return 'down'
        if dir == 'down': return 'up'
