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
        self.fes.put((0, self.arrival, (lamp, lamp.randomNeigh(), randint(3, 10), 1)))  # primo elemento
        lamp = self.city.randomLamp()
        self.fes.put((50, self.failure, lamp))
        for i in range(len(self.city.lampioni)):    # per accendere tutti i lampioni a inizio simulazione
            self.city.searchLampById(self.city.lampioni[i]).setLevel(self.scheduler.lampValueBase(self.clock, False),self.clock)
            self.city.searchLampById(self.city.lampioni[i]).setState('on')
        while self.clock < self.duration:
            for i in range(10):
                print(self.city.matrix[2,i].getLevel(),' - ', end="")
            (self.clock, event, attr) = self.fes.get()
            flag_suntime, flag_day = self.scheduler.checksuntime(self.clock)
            if flag_day:
                for i in range(len(self.city.lampioni)):    # per aggiornare tutti i lampioni quando cambia giorno
                    if  self.city.searchLampById(self.city.lampioni[i]) not in self.lampsOn: # controllo se è attivo perchè c'è auto
                        if self.city.searchLampById(self.city.lampioni[i]).getState()=='True' :
                            self.city.searchLampById(self.city.lampioni[i]).setLevel(self.scheduler.lampValueBase(self.clock, True),self.clock)
                        else :
                            self.city.searchLampById(self.city.lampioni[i]).setLevel(self.scheduler.lampValueBase(self.clock, False),self.clock)
                    else:
                        if self.city.searchLampById(self.city.lampioni[i]).getState()=='True' :
                            self.city.searchLampById(self.city.lampioni[i]).setLevel(self.scheduler.lampValueCar(self.clock, True),self.clock)
                        else :
                            self.city.searchLampById(self.city.lampioni[i]).setLevel(self.scheduler.lampValueCar(self.clock, False),self.clock)
            if flag_suntime:
                event(attr)

       
            

        print("arrivi -- ", self.narrivi)
        print("fails -- ", self.nfails)

    def shift(self, attributes):
        lamp, direction, ttl, carid, arrival_lamp = attributes
        fault = False
        for item in lamp.neigh.values():
            if item.getState() == 'fail':
                fault = True
        arrival_lamp.setBusy(0)  # setto il lampione di arrivo a 0 (non ho auto)
        lamp.setBusy(1)
        print('la macchina, ', carid,' si sposta al lampione ', lamp.id, 'e va verso ', direction, 'al lampione',
              lamp.neigh[direction].id, 'con ttl ', ttl)
        if ttl > 0:  # controllo se la macchina ha ancora time to live
            nextLamp = lamp.neigh[direction]
            fault2=False
            for item2 in nextLamp.neigh.values():
                if item2.getState() == 'fail':
                    fault2 = True
            if nextLamp.getState() != 'fail':
                nextLamp.setLevel(self.scheduler.lampValueCar(self.clock, fault2),self.clock)
                if nextLamp not in self.lampsOn:
                    self.lampsOn.append(nextLamp)
            else:
                lamp.setLevel(self.scheduler.lampValueCar(self.clock, fault),self.clock)
            try:  # next shift
                self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                            (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
            except:
                self.fes.put((self.scheduler.shiftTime(self.clock), self.out,
                            (carid, nextLamp, lamp)))
                print('STA PER USCIRE FUORI DAL SISTEMA')

        # print('vecchi')
        # print([item.id for item in self.lampsOn])
        lampsOn_temp = self.lampsOn.copy()
        for item in self.lampsOn:
            fault = False
            for item2 in item.neigh.values():
                if item2.getState() == 'fail':
                    fault = True
            flag = 0
            for neigh in item.neigh.values():
                if neigh.busy > 0 or item.busy > 0:
                    flag = 1
            if flag == 0:
                item.setLevel(self.scheduler.lampValueBase(self.clock, fault),self.clock)
                lampsOn_temp.remove(item)
        self.lampsOn = lampsOn_temp.copy()
        # print('nuovi')
        # print([item.id for item in self.lampsOn])
        print('i lampioni accesi sono : ', [(item.id, item.lev) for item in self.lampsOn])

    def out(self, attributes):
        carid, lamp, arrival_lamp = attributes
        fault = False
        for item in lamp.neigh.values():
            if item.getState() == 'fail':
                fault = True
        print('la macchina ',carid,' sparisce dopo il lampione', lamp.id)
        arrival_lamp.setBusy(0)  # setto il lampione di arrivo a 0 (non ho auto)
        # flag = 0
        # for neigh in lamp.neigh.values():
        #     if neigh.busy > 0:
        #         flag = 1
        #     else:
        #         neigh.setLevel(self.scheduler.lampValueBase(self.clock, fault))
        # if flag == 0:
        #     lamp.setLevel(self.scheduler.lampValueBase(self.clock, fault))
        #     self.lampsOn.remove(lamp)

        
        lampsOn_temp = self.lampsOn.copy()
        for item in self.lampsOn:
            flag = 0
            for neigh in item.neigh.values():
                if neigh.busy > 0:
                    flag = 1
            if flag == 0:
                item.setLevel(self.scheduler.lampValueBase(self.clock, fault),self.clock)
                lampsOn_temp.remove(item)
        self.lampsOn = lampsOn_temp.copy()


        print('i lampioni accesi sono : ', [(item.id, item.lev) for item in self.lampsOn])

    def arrival(self, attributes):

        """--->setto la luminosità di tutti i lampioni intorno"""
        lamp, direction, ttl, carid = attributes

        print('arriva la macchina ', carid, 'al lampione ', lamp.id,' al tempo ', self.clock, 'e si sposta verso ',
              direction, ',verso il lampione ', lamp.neigh[direction].id, 'con ttl ', ttl)

        fault = False
        for item in lamp.neigh.values():
            if item.getState() == 'fail':
                fault = True
        if lamp.getState() != 'fail':
            lamp.setLevel(self.scheduler.lampValueCar(self.clock, fault),self.clock)
            if lamp not in self.lampsOn:
                self.lampsOn.append(lamp)
        else: fault = True

        lamp.setBusy(1)
        for neigh in lamp.neigh.values():
            if neigh.getState() != 'fail':
                neigh.setLevel(self.scheduler.lampValueCar(self.clock, fault),self.clock)
                if neigh not in self.lampsOn:
                    self.lampsOn.append(neigh)
            else: #qui
                lamp.setLevel(self.scheduler.lampValueCar(self.clock, fault),self.clock)
        print('i lampioni accesi sono : ', [(item.id, item.lev) for item in self.lampsOn])
        """--->schedulo il prossimo shift"""
        try:
            nextLamp = lamp.neigh[direction]
            self.fes.put((self.scheduler.shiftTime(self.clock), self.shift,
                          (nextLamp, nextLamp.randomNeigh(direction),
                           ttl - 1, carid, lamp)))
        except:
            pass

        """--> schedulo il next arrival"""
        nextArrival = self.city.randomLamp()
        try:
            self.fes.put((self.scheduler.arrivalTime(self.clock), self.arrival,
                          (nextArrival, nextArrival.randomNeigh(),
                           randint(3, 10), carid + 1)))
        except:
            pass
        self.narrivi += 1

    def failure(self, attributes):

        lamp = attributes
        lamp.setLevel(0,self.clock)
        lamp.setState('fail')
        print('\n\n Cè STATO UN FAULT NEL LAMPIONE ', lamp.id)
        for neigh in lamp.neigh.values():
            if neigh.getState() != 'fail':
                neigh.setLevel(self.scheduler.lampValueBase(self.clock, True),self.clock)
        self.fes.put((self.clock + expovariate(1.0 / self.scheduler.repair_parameter), self.repair, lamp))
        """schedule next failure"""
        nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((self.clock + expovariate(1.0 / self.scheduler.fail_parameter), self.failure, nextLamp))
        self.nfails += 1

    def repair(self, attributes):
        lamp = attributes
        print('\n\n Cè STATO LA RIPARAZIONE DEL  LAMPIONE ', lamp.id)
        lamp.setState('on')
        lamp.setLevel(self.scheduler.lampValueBase(self.clock, False),self.clock)
        for neigh in lamp.neigh.values():
            flag = False
            for el in self.lampsOn: 
                if neigh == el: 
                    neigh.setLevel(self.scheduler.lampValueCar(self.clock, False),self.clock)
                    flag = True
            if flag == False:  
                neigh.setLevel(self.scheduler.lampValueBase(self.clock, False),self.clock)
                