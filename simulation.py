from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd

from scheduler import Scheduler


class Simulation:

    def __init__(self, schedules,duration, city, seed=0):
        self.duration = duration
        self.clock = 0
        self.city = city
        self.fes = PriorityQueue()  # nella mia fes posso avere due tipi di eventi : arrivo di una macchina o un fail
        # del lampione
        self.base_value = 0
        rd.seed(seed)
        self.nfails = 0
        self.narrivi = 0
        self.scheduler = schedules

    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """
        lamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((0, self.arrival, (lamp, choice(list(lamp.neigh.keys())), randint(3, 10))))  # primo elemento
        lamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((50, self.failure, lamp))
        while self.clock < self.duration:
            (self.clock, event, attr) = self.fes.get()
            if self.scheduler.checksuntime(self.clock):
                event(attr)

        print("arrivi -- ", self.narrivi)
        print("fails -- ", self.nfails)




    def shift(self, attributes):
        lamp, direction, ttl = attributes
        print('la macchina si sposta al lampione ', lamp.id)
        if ttl > 0:  # controllo se la macchina ha ancora time to live
            nextLamp = lamp.neigh[direction]
            nextLamp.setLevel(1.2 * self.base_value)
            try:  # next shift
                self.fes.put(
                    (self.clock + expovariate(self.scheduler.shift_parameter(self.clock)), self.shift, (
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
        print('arriva una macchina al lampione ', lamp.id)
        """--->schedulo il prossimo shift"""
        try:
            nextLamp = lamp.neigh[direction]
            self.fes.put((self.clock + expovariate(self.scheduler.shift_parameter(self.clock)), self.shift, (
                nextLamp, choice(list(filter(lambda x: x != self.opposite(direction), nextLamp.neigh.keys()))),
                ttl - 1)))
        except:
            pass

        """--> schedulo il next arrival"""
        nextArrival = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        try:
            self.fes.put((self.clock + expovariate(self.scheduler.arrival_parameter(self.clock)), self.arrival,
                          (nextArrival, choice(list(nextArrival.neigh.keys())),
                           randint(3, 10))))
        except:
            pass
        self.narrivi += 1





    def failure(self, attributes):
        lamp = attributes
        lamp.setState('off')
        for neigh in lamp.neigh.values():
            neigh.setLevel(1.2 * self.base_value)
        self.fes.put((self.clock + expovariate(1.0 / self.scheduler.repair_parameter), self.repair, lamp))
        """schedule next failure"""
        nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((self.clock + expovariate(1.0 / self.scheduler.fail_parameter), self.failure, nextLamp))
        self.nfails += 1

    def repair(self, attributes):
        lamp = attributes
        lamp.setState('on')
        for neigh in lamp.neigh.values():
            neigh.setLevel(self.base_value)

    def dailyUpdate(self):
        """ aggiorniamo il valore  base value"""

        self.scheduler.newDay()

        if self.dati['meteo'] == 'sole':
            self.base_value = 50
        if self.dati['meteo'] == 'pioggia/temporale':
            self.base_value = 60
        if self.dati['meteo'] == 'pioggia/neve':
            self.base_value = 70
        if self.dati['meteo'] == 'pioggia/nebbia':
            self.base_value = 80
        if self.dati['meteo'] == 'pioggia':
            self.base_value = 85
        if self.dati['meteo'] == 'neve/nebbia':
            self.base_value = 90
        if self.dati['meteo'] == 'nebbia':
            self.base_value = 95
        self.city.updateState()

    def opposite(self, dir):
        if dir == 'left': return 'right'
        if dir == 'rigth': return 'left'
        if dir == 'up': return 'down'
        if dir == 'down': return 'up'
