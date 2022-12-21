from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd
import matplotlib.pyplot as plt

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
        """cosa succede al tramonto --->li metto tutti al valore base"""
        self.flag = True
        for lamp in self.city.allLamps():
            fault = lamp.checkNeighState()  # controllo se tra i vicini c'è un fault
            if lamp.getState() != 'fail':  # se il mio lampione è funzionante, aggiunsto  valore in base anche ai vicini
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
        # print(self.clock,' MEZZANOTTE')
        """cosa succede a mezzanotte: aggiorno i valori base di tutti i lampioni"""
        [lamps.setLevel(self.scheduler.lampValueBase(self.clock, False), self.clock) for lamps in self.city.allLamps()
         if lamps not in self.lampsOn and lamps.getState() != 'fail']
        self.fes.put((self.clock + 24 * 3600,1, self.midnight, None))  # schedulo la prossima mezzanotte

        # maxCambi = 0 
        # for lamp in self.city.allLamps():
        #     if maxCambi < lamp.getCambio():  
        #         maxCambi = lamp.getCambio()
        #         id_c = lamp.getID()
        # print('ID ', id_c, ' cambi ', maxCambi)
        levs, clk = self.city.searchLampById(783).load_profile()
        print(levs,'\n',clk)
        plt.plot(clk, levs)
        plt.show()
    






    def sunrise(self, attributes):
        # print(self.clock,'  ALBA')
        """ cosa succede all'alba: spengo tutti i lampioni, li setto tutti a zero e schedulo il prossimo evento al
        tramonto """
        self.flag = False

        for lamp in self.city.allLamps():
            lamp.setLevel(0, self.clock)
            lamp.setBusy(-1)
        nextlamp = self.city.randomLamp()
        self.fes.put((self.clock + 12 * 3600, 3,self.arrival, (nextlamp, nextlamp.randomNeigh(), randint(3, 10), 1)))   # carid da aggiustare
        value=self.scheduler.nextSunrise()
        self.fes.put((value,1, self.sunrise, None))  # schedule next sunrise




    def sunset(self, attibutes):
        """cosa succede al tramonto --->li metto tutti al valore base"""
        # print(self.clock,' TRAMONTO')
        self.flag = True
        for lamp in self.city.allLamps():
            fault = lamp.checkNeighState()   # controllo se tra i vicini c'è un fault
            if lamp.getState() != 'fail':  # se il mio lampione è funzionante, aggiunsto  valore in base anche ai vicini
                lamp.setLevel(self.scheduler.lampValueBase(self.clock, fault), self.clock)
        # schedulo la prossima sunset
        value=self.scheduler.nextSunset()
        self.fes.put((value,1, self.sunset, None))





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
        self.fes.put((1, 3,self.arrival, (lamp, lamp.randomNeigh(), randint(3, 10), 1)))  # primo elemento
        lamp = self.city.randomLamp()
        self.fes.put((50,2,self.failure, lamp))
        # prima sunrise
        self.fes.put((29280,1, self.sunrise, None))
        # prima mezzanotte
        self.fes.put((86400, 1,self.midnight, None))
        # prima sunset
        self.fes.put((61080,1, self.sunset, None))




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
                # print('TEMPO :', self.clock, ')) la macchina, ', carid, ' si sposta al lampione ', lamp.id,
                #       'e va verso ', direction, 'al lampione',
                #       lamp.neigh[direction].id, 'con ttl ', ttl, end="---->  ")
                nextLamp = lamp.neigh[direction]
                self.lampTurnOn(nextLamp)
                try: self.fes.put((self.scheduler.shiftTime(self.clock), 4,self.shift,
                                  (nextLamp, nextLamp.randomNeigh(direction), ttl - 1, carid, lamp)))
                except: lamp.setBusy(0)
            else:
                  lamp.setBusy(0)
                  # print('TEMPO :', self.clock, '))LA MACCHINA SCOPARE DAL SISTEMA ', end="---->  ")
            self.disableLamps()



    def arrival(self, attributes):
        """arriva una nuova macchina, accendo il lampione e tutti i suoi vicini, schedulo il prossio shift e arrivo"""
        if self.flag:
            self.disableLamps()
            lamp, direction, ttl, carid = attributes
            # print('TEMPO :' ,self.clock,')) arriva la macchina ', carid, 'al lampione ', lamp.id, 'e si sposta verso ',
            #       direction, ',verso il lampione ', lamp.neigh[direction].id, 'con ttl ', ttl, end="---->  ")
            self.lampTurnOn(lamp)  # accendo il lampione e lo setto busy
            lamp.setBusy(1)
            for neigh in lamp.neigh.values():  self.lampTurnOn(neigh) #accendo tutti i vicini
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
        if self.flag:
            lamp = attributes
            # print('TEMPO :' ,self.clock,'))  Cè STATO UN FAULT NEL LAMPIONE ', lamp.id, end="---->  ")
            lamp.setLevel(0, self.clock)
            lamp.setState('fail')

            for neigh in lamp.neigh.values():
                if neigh.getState() != 'fail':
                    neigh.setLevel(self.scheduler.lampValueBase(self.clock, True), self.clock)
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.repair_parameter), 2,self.repair, lamp))
            """schedule next failure"""
            nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
            self.fes.put((self.clock + expovariate(1.0 / self.scheduler.fail_parameter),2, self.failure, nextLamp))
            self.nfails += 1





    def repair(self, attributes):
        lamp = attributes
        lamp.setState('on')
        # print('TEMPO :' ,self.clock,')) Cè STATO LA RIPARAZIONE DEL  LAMPIONE ', lamp.id, end=" ----->")
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




