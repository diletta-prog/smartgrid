from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd

from scheduler import Scheduler


class Simulation:


    def __init__(self, schedules, duration, city, seed=0):
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
        self.lampsOn = []

    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """

        lamp = self.city.randomLamp()
        self.fes.put((0, self.arrival, (lamp, lamp.randomNeigh(), randint(3, 10),1)))  # primo elemento
        lamp = self.city.randomLamp()
        self.fes.put((50, self.failure, lamp))

        while self.clock < self.duration:
            (self.clock, event, attr) = self.fes.get()
            if self.scheduler.checksuntime(self.clock):
                event(attr)

        print("arrivi -- ", self.narrivi)
        print("fails -- ", self.nfails)

    def shift(self, attributes):
        lamp, direction, ttl,carid, arrival_lamp = attributes
        fault = 0
        for item in lamp.neigh.values():
            if item.getState() == 'fail':
                fault = 1
        arrival_lamp.setBusy(0) # setto il lampione di arrivo a 0 (non ho auto)
        lamp.setBusy(1)
        #print('la macchina, ', carid,' si sposta al lampione ', lamp.id, 'e va verso ', direction, 'al lampione',lamp.neigh[direction].id, 'con ttl ', ttl)
        if ttl > 0:  # controllo se la macchina ha ancora time to live
            nextLamp = lamp.neigh[direction]
            nextLamp.setLevel(self.scheduler.lampValueCar(self.clock,fault))
            self.lampsOn.append(nextLamp)
            try:  # next shift
                self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                              (nextLamp, nextLamp.randomNeigh(direction), ttl - 1,carid,lamp)))
            except:
                pass
        
        # print('vecchi')
        # print([item.id for item in self.lampsOn])
        lampsOn_temp = self.lampsOn.copy()
        for item in self.lampsOn:
            flag = 0
            for neigh in item.neigh.values():
                if neigh.busy == 1 or item.busy == 1:
                    flag = 1
            if flag == 0:
                item.setLevel(self.scheduler.lampValueBase(self.clock,fault)) 
                lampsOn_temp.remove(item)
        self.lampsOn = lampsOn_temp.copy()
        # print('nuovi')
        # print([item.id for item in self.lampsOn])


                


    def arrival(self, attributes):

        """--->setto la luminosità di tutti i lampioni intorno"""
        lamp, direction, ttl ,carid = attributes
        fault = 0
        for item in lamp.neigh.values():
            if item.getState() == 'fail':
                fault = 1
        lamp.setLevel(self.scheduler.lampValueCar(self.clock,fault)) 
        self.lampsOn.append(lamp)
        lamp.setBusy(1)
        for neigh in lamp.neigh.values():
            neigh.setLevel(self.scheduler.lampValueCar(self.clock,fault))
            self.lampsOn.append(neigh)
        #print('arriva la macchina ',carid,' al lampione ', lamp.id, 'e va verso ', direction,'al lampione',lamp.neigh[direction].id, 'con ttl ', ttl)
        """--->schedulo il prossimo shift"""
        try:
            nextLamp = lamp.neigh[direction]
            self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                          (nextLamp, nextLamp.randomNeigh(direction),
                         ttl - 1,carid,lamp)))
        except:
            pass

        """--> schedulo il next arrival"""
        nextArrival = self.city.randomLamp()
        try:
            self.fes.put((self.scheduler.arrivalTime(self.clock), self.arrival,
                          (nextArrival, nextArrival.randomNeigh(),
                           randint(3, 10),carid+1)))
        except:
            pass
        self.narrivi += 1

    def failure(self, attributes):
        lamp = attributes
        lamp.setState('fail')
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



    
