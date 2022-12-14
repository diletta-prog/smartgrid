from queue import PriorityQueue
from random import randint, expovariate


class Simulation:

    def __init__(self, duration, city, arrival_parameter, fail_parameter, seed=0):
        self.duration = duration
        self.clock = 0
        self.seed = seed
        self.city = city
        self.fes = PriorityQueue()  # nella mia fes posso avere due tipi di eventi : arrivo di una macchina o un fail
        # del lampione
        self.arrival_parameter = arrival_parameter
        self.fail_parameter = fail_parameter

    def start(self):
        """ cuore della simulazione, prende iterativamente elementi dalla fes e agisce in base al tipo di evento """

        lamp = randint(0, self.city.lampsCount)
        self.fes.put((0, "arrival", lamp))  # primo elemento
        while self.clock < self.duration:
            (self.clock, event_type, lamp) = self.fes.get()
            if event_type == 'arrival':
                self.arrival(lamp)
            if event_type == 'failure':
                self.failure(lamp)

    def arrival(self, lamp):
        """cosa facciamo in caso di un arrivo (macchina o pedone) in posizione pos
        --> aumento l'intensità del lampione e dei vicini



        --> schedulo il next arrival"""
        self.fes.put((self.clock + expovariate(1.0 / self.arrival_parameter), "arrival",
                      randint(0, self.city.lampsCount)))
        pass

    def failure(self, pos):
        """cosa facciamo in caso di una failure dle lampione in posizione pos
        --> aumento l'intensità dei vicini


        --> schedulo il next fail """
        self.fes.put((self.clock + expovariate(1.0 / self.fail_parameter), "failure", randint(0, self.city.lampsCount)))
