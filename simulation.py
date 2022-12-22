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
        """Main part of the simulation, 
            iteratively takes elements from the fes and acts according to the type of event"""
        self.fesInit()
        self.flag = True
        for lamp in self.city.allLamps():
            #look for a fault in the neighbours
            fault = lamp.checkNeighState()  
            # the streetlight works correctly -- > set the base value taking into account the neighbours 
            if lamp.getState() != 'fail':  
                lamp.setLevel(self.scheduler.lampValueBase(self.clock, fault), self.clock)
        while self.clock < self.duration:
            # print(list(self.fes.queue))
            # for i in range(10):
            #     print(self.city.matrix[2, i].getLevel(), ' - ', end="")
            # print("\n")
            try:
             (self.clock,prior, event, attr) = self.fes.get()
            except:
                print(self.fes.queue)
            event(attr)
        self.printStats()


    def midnight(self, attributes):
        """Event: midnight, update all the lampposts base value"""
        [lamps.setLevel(self.scheduler.lampValueBase(self.clock, False), self.clock) for lamps in self.city.allLamps()
         if lamps not in self.lampsOn and lamps.getState() != 'fail']
        self.fes.put((self.clock + 24 * 3600,1, self.midnight, None))  # schedulo la prossima mezzanotte


    def sunrise(self, attributes):
        """Event: sunrise, turn off all lampposts and schedule the first arrival at sunset"""
        self.flag = False
        for lamp in self.city.allLamps():
            lamp.setLevel(0, self.clock)
            lamp.setBusy(-1)
        nextlamp = self.city.randomLamp()
        self.fes.put((self.clock + 12 * 3600, 3,self.arrival, (nextlamp, nextlamp.randomNeigh(), randint(3, 10), 1))) 
        self.fes.put((self.clock + 12 * 3600,2,self.failure, lamp))
        value=self.scheduler.nextSunrise()
        # schedule next sunrise
        self.fes.put((value,1, self.sunrise, None)) 


    def sunset(self, attibutes):
        """Event: sunset, set all lampposts to base value"""
        self.flag = True
        for lamp in self.city.allLamps():
            # look for a fault in the nearby lampposts
            fault = lamp.checkNeighState()  
            # the streetlight works correctly -- > set the base value taking into account the neighbours 
            if lamp.getState() != 'fail':
                lamp.setLevel(self.scheduler.lampValueBase(self.clock, fault), self.clock) 
        value=self.scheduler.nextSunset()
        # schedule next sunset
        self.fes.put((value,1, self.sunset, None)) 


    def lampTurnOn(self, lamp):
        """taking into account the neighbours valeu, it turns on the streetlight"""
        # look for a fault in the nearby lampposts
        fault = lamp.checkNeighState()
        # the streetlight works correctly -- > set the base value taking into account the neighbours
        if lamp.getState() != 'fail':
            lamp.setLevel(self.scheduler.lampValueCar(self.clock, fault), self.clock)
            if lamp not in self.lampsOn:
                self.lampsOn.append(lamp)


    def disableLamps(self):
        """"check whether there are any inactive lamps that need to be set to the base value"""
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
        """initialises the values in the fes"""
        lamp = self.city.randomLamp()
        # first element
        self.fes.put((1, 3,self.arrival, (lamp, lamp.randomNeigh(), randint(3, 10), 1)))  
        lamp = self.city.randomLamp()
        self.fes.put((50,2,self.failure, lamp))
        # fisrt sunrise
        self.fes.put((29280,1, self.sunrise, None))
        # first mezzanotte
        self.fes.put((86400, 1,self.midnight, None))
        # first sunset
        self.fes.put((61080,1, self.sunset, None))


    def printStats(self):
        print("Total number of cars registrered in the system -- ", self.narrivi)
        print("Total number of broken lampposts  -- ", self.nfails)


    def shift(self, attributes):
        """la macchina passa in un nuovo nodo, aumento il valore del successivo, schedulo prossimo shift"""
        if self.flag:

            lamp, direction, ttl, carid, arrival_lamp = attributes

            arrival_lamp.setBusy(0)  # setto il lampione di arrivo a 0 (non ho auto)
            lamp.setBusy(1)
            # check time to live
            if ttl > 0:  
                # print('At time :', self.clock, ')) the cars, ', carid, ' move toward', lamp.id,
                #       'and continues towards', direction, 'to lamppost',
                #       lamp.neigh[direction].id, 'with ttl ', ttl, end="---->  ")
                nextLamp = lamp.neigh[direction]
                self.lampTurnOn(nextLamp)
                try: self.fes.put((self.scheduler.shiftTime(self.clock), 4,self.shift,
                                  (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
                except: lamp.setBusy(0)
            else:
                  lamp.setBusy(0)
                  # print('At time :', self.clock, '))the car exits the system ', end="---->  ")
            self.disableLamps()


    def arrival(self, attributes):
        """Event: a car is detected, turn on the lamppost and its neighbours, schedule the next shift event and arrival event"""
        if self.flag:
            self.disableLamps()
            lamp, direction, ttl, carid = attributes
            # print('At time :' ,self.clock,')) the car ', carid, ' reach the lamppost ', lamp.id, 'and move towards ',
            #       direction, ',to the lamppost', lamp.neigh[direction].id, 'with ttl ', ttl, end="---->  ")
           
            # turn on the lamppost and set it to busy
            self.lampTurnOn(lamp)  
            lamp.setBusy(1)

            #turn onn all the neighbours
            for neigh in lamp.neigh.values():  self.lampTurnOn(neigh)
            nextLamp = lamp.neigh[direction]
            try: self.fes.put((self.scheduler.shiftTime(self.clock),4, self.shift,
                              (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
            except: lamp.setBusy(0)
            nextArrival = self.city.randomLamp()
            try:  self.fes.put((self.scheduler.arrivalTime(self.clock),3, self.arrival,
                              (nextArrival, nextArrival.randomNeigh(), randint(3, 10), carid + 1)))
            except: pass
            self.narrivi += 1



    def failure(self, attributes):
        """Event: fault in a lamppost"""
        if self.flag:
            lamp = attributes
            # print('At time :' ,self.clock,')) a fault turn off the lamppost ', lamp.id, end="---->  ")
            lamp.setLevel(0, self.clock)
            lamp.setState('fail')

            for neigh in lamp.neigh.values():
                if neigh.getState() != 'fail':
                    neigh.setLevel(self.scheduler.lampValueBase(self.clock, True), self.clock)
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.repair_parameter), 2,self.repair, lamp))
            # schedule next failure
            nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.fail_parameter),2, self.failure, nextLamp))
            self.nfails += 1


    def repair(self, attributes):
        """Event: a lamppost is repaired"""
        lamp = attributes
        lamp.setState('on')
        # print('At time :' ,self.clock,')) is repaired the lamppost ', lamp.id, end=" ----->")
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




