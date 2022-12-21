from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd

from scheduler import Scheduler


class Simulation:

    def __init__(self, schedules, duration, city, seed=0):
        self.duration = duration
        self.clock = 0
        self.city = city
        self.fes = PriorityQueue()
        self.base_value = 0
        rd.seed(seed)
        self.nfails = 0
        self.narrivi = 0
        self.scheduler = schedules
        self.lampsOn = []
        self.flag = True




    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """
        self.fesInit()
        while self.clock < self.duration:
            (self.clock, event, attr) = self.fes.get()
            event(attr)
        self.printStats()




    def midnight(self, attributes):
        """cosa succede a mezzanotte: aggiorno i valori base di tutti i lampioni"""
        [lamps.setLevel(self.scheduler.lampValueBase(self.clock, False), self.clock) for lamps in self.city.allLamps()
         if lamps not in self.lampsOn and lamps.getState() != 'fail']
        self.fes.put((self.clock + 24 * 3600, self.midnight, None))  # schedulo la prossima mezzanotte






    def sunrise(self, attributes):
        """ cosa succede all'alba: spengo tutti i lampioni, li setto tutti a zero e schedulo il prossimo evento al
        tramonto """
        self.flag = False
        for lamp in self.city.allLamps():
            lamp.setLevel(0, self.clock)
            lamp.setBusy(-1)
        nextlamp = self.city.randomLamp()
        self.fes.put((self.clock + 12 * 3600, self.arrival, (nextlamp, nextlamp.randomNeigh(), randint(3, 10), 1)))   # carid da aggiustare
        self.fes.put((self.clock + 24 * 3600, self.sunrise, None))  # schedule next sunrise





    def sunset(self, attibutes):
        """cosa succede al tramonto --->li metto tutti al valore base"""
        self.flag = True
        for lamp in self.city.allLamps():
            fault = lamp.checkNeighState()   # controllo se tra i vicini c'è un fault
            if lamp.getState() != 'fail':  # se il mio lampione è funzionante, aggiunsto  valore in base anche ai vicini
                lamp.setLevel(self.scheduler.lampValueBase(self.clock, fault), self.clock)
        # schedulo la prossima sunset
        self.fes.put((self.clock + 24 * 3600, self.sunset, None))





    def lampTurnOn(self, lamp):
        """accendo il lampione, in base al valore dei vicini"""
        # controllo se tra i vicini c'è un fault
        fault = lamp.checkNeighState()
        # se il mio lampione è funzionante, aggiunsto il valore in base anche ai vicini
        if lamp.getState() != 'fail':
            lamp.setLevel(self.scheduler.lampValueCar(self.clock, fault), self.clock)
            if lamp not in self.lampsOn:
                self.lampsOn.append(lamp)





    def disableLamps(self):
        """controlla se ci sono lampioni idle che devono essere rimessi al valore base"""
        lampsOn_temp = self.lampsOn.copy()
        for item in self.lampsOn:
            fault = item.checkNeighState()
            flag = 0
            for neigh in item.neigh.values():
                if neigh.busy > 0 or item.busy > 0:
                    flag = 1
            if flag == 0:
                item.setLevel(self.scheduler.lampValueBase(self.clock, fault), self.clock)
                lampsOn_temp.remove(item)
        self.lampsOn = lampsOn_temp.copy()





    def fesInit(self):
        """inizializzo i valori nella fes"""
        lamp = self.city.randomLamp()
        self.fes.put((0, self.arrival, (lamp, lamp.randomNeigh(), randint(3, 10), 1)))  # primo elemento
        lamp = self.city.randomLamp()
        self.fes.put((50, self.failure, lamp))
        # prima sunrise
        self.fes.put((29280, self.sunrise, None))
        # prima mezzanotte
        self.fes.put((86400, self.midnight, None))
        # prima sunset
        self.fes.put((61080, self.sunset, None))




    def printStats(self):
        print("arrivi -- ", self.narrivi)
        print("fails -- ", self.nfails)




    def shift(self, attributes):
        """la macchina passa in un nuovo nodo, aumento il valore del successivo, schedulo prossimo shift"""
        if self.flag:
            lamp, direction, ttl, carid, arrival_lamp = attributes
            arrival_lamp.setBusy(0)  # setto il lampione di arrivo a 0 (non ho auto)
            lamp.setBusy(1)
            if ttl > 0:  # controllo se la macchina ha ancora time to live
                nextLamp = lamp.neigh[direction]
                self.lampTurnOn(nextLamp)
                try: self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                                  (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
                except: lamp.setBusy(0)
            else: lamp.setBusy(0)
            self.disableLamps()



    def arrival(self, attributes):
        """arriva una nuova macchina, accendo il lampione e tutti i suoi vicini, schedulo il prossio shift e arrivo"""
        if self.flag:
            lamp, direction, ttl, carid = attributes
            self.lampTurnOn(lamp)  # accendo il lampione e lo setto busy
            lamp.setBusy(1)
            for neigh in lamp.neigh.values():  self.lampTurnOn(neigh) #accendo tutti i vicini
            nextLamp = lamp.neigh[direction]
            try: self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                              (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
            except: pass
            nextArrival = self.city.randomLamp()
            try:  self.fes.put((self.scheduler.arrivalTime(self.clock), self.arrival,
                              (nextArrival, nextArrival.randomNeigh(), randint(3, 10), carid + 1)))
            except: pass
            self.narrivi += 1






    def failure(self, attributes):
        if self.flag:
            lamp = attributes
            lamp.setLevel(0, self.clock)
            lamp.setState('fail')

            for neigh in lamp.neigh.values():
                if neigh.getState() != 'fail':
                    neigh.setLevel(self.scheduler.lampValueBase(self.clock, True), self.clock)
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.repair_parameter), self.repair, lamp))
            """schedule next failure"""
            nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.fail_parameter), self.failure, nextLamp))
            self.nfails += 1





    def repair(self, attributes):
        lamp = attributes
        lamp.setState('on')
        if self.flag:
            lamp.setLevel(self.scheduler.lampValueBase(self.clock, False), self.clock)
            for neigh in lamp.neigh.values():
                flag = False
                for el in self.lampsOn:
                    if neigh == el:
                        neigh.setLevel(self.scheduler.lampValueCar(self.clock, False), self.clock)
                        flag = True
                if not flag:
                    neigh.setLevel(self.scheduler.lampValueBase(self.clock, False), self.clock)




