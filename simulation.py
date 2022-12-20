from queue import PriorityQueue
from random import randint, expovariate, choice, seed
import random as rd


class Simulation:

    def __init__(self,dati, duration, city, arrival_parameters, shift_parameters, fail_parameter=518400, repair_parameter=100, seed=0):
        self.duration = duration
        self.clock = 0
        self.seed = seed
        self.city = city
        self.fes = PriorityQueue()  # nella mia fes posso avere due tipi di eventi : arrivo di una macchina o un fail
        # del lampione
        self.arrival_parameters = arrival_parameters
        self.fail_parameter = fail_parameter
        self.base_value = 0
        self.shift_parameters = shift_parameters
        self.repair_parameter = repair_parameter 
        rd.seed(seed)
        self.hist_arrival_index = 0 
        self.hist_shift_index = 0 
        self.index_day = 0 
        self.day = 0

        self.nfails = 0 
        self.narrivi = 0
        self.dati = dati




    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """
        lamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((0, self.arrival, (lamp, choice(list(lamp.neigh.keys())), randint(3, 10))))  # primo elemento
        lamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((50, self.failure, lamp))
        while self.clock < self.duration:
            (self.clock, event, attr) = self.fes.get()
            if self.checksuntime() : 
                event(attr)

        print("arrivi -- ", self.narrivi)
        print("arrivi -- ", self.nfails)


    def checksuntime(self):
        row = self.dati.iloc[self.day]
        flag = True
        if self.clock > row['SUNRISE'] and self.clock < row['SUNSET']: 
            flag = False
        return flag


    def shift(self, attributes):
        lamp, direction, ttl = attributes
        if ttl > 0:  # controllo se la macchina ha ancora time to live
            for index, el in self.shift_parameters[self.hist_shift_index:].iterrows():
                if self.clock < el['range']: 
                    shift_parameter = el['lambda']
                    break
            self.hist_shift_index = index
            nextLamp = lamp.neigh[direction]
            nextLamp.setLevel(1.2 * self.base_value)
            try:  # next shift
                self.fes.put(
                    (self.clock + expovariate(1.0 / shift_parameter), self.shift, (
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

        """--->schedulo il prossimo shift"""
        for index, el in self.shift_parameters[self.hist_shift_index:].iterrows():
            if self.clock < el['range']: 
                shift_parameter = el['lambda']
                break
        self.hist_shift_index = index
        try:
            nextLamp = lamp.neigh[direction]
            self.fes.put((self.clock + expovariate(1.0 / shift_parameter), self.shift, (
                nextLamp, choice(list(filter(lambda x: x != self.opposite(direction), nextLamp.neigh.keys()))),
                ttl - 1)))
        except:
            pass

        """--> schedulo il next arrival"""
        nextArrival = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        
        for index, el in self.arrival_parameters[self.hist_arrival_index:].iterrows():
            if self.clock < el['range']: 
                arrival_parameter = el['lambda']
                break
        self.hist_arrival_index = index
        try:
            self.fes.put((self.clock + expovariate(arrival_parameter), self.arrival,
                          (nextArrival, choice(list(nextArrival.neigh.keys())),
                           randint(3, 10))))
        except:
            print(nextArrival.id, nextArrival.neigh)
        self.narrivi += 1 




    def failure(self, attributes):
        lamp = attributes
        lamp.setState('off')
        for neigh in lamp.neigh.values():
            neigh.setLevel(1.2 * self.base_value)
        self.fes.put((self.clock + expovariate(1.0 / self.repair_parameter), self.repair, lamp))
        """schedule next failure"""
        nextLamp = self.city.searchLampById(randint(0, self.city.lampsCount - 1))
        self.fes.put((self.clock + expovariate(1.0 / self.fail_parameter), self.failure, nextLamp))
        self.nfails += 1 


    def repair(self, attributes):
        lamp = attributes
        lamp.setState('on')
        for neigh in lamp.neigh.values():
            neigh.setLevel(self.base_value)


    def dailyUpdate(self):
        """ aggiorniamo il valore  base value"""
        
        self.index_day +=1
        self.day = self.data.index[self.index_day]

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
