from random import expovariate


class Scheduler:
    def __init__(self, dati, shift_parameters, arrival_parameters, fail_parameter, repair_parameter):
        self.dati = dati
        self.shift_parameters = shift_parameters
        self.arrival_parameters = arrival_parameters
        self.fail_parameter = fail_parameter
        self.repair_parameter = repair_parameter
        self.hist_shift_index = 0
        self.hist_arrival_index = 0
        self.day = 0

    def checksuntime(self, clock):
        # row = self.dati.iloc[self.day]
        # if row['SUNRISE'] < clock < row['SUNSET']:
        #     return False
        return True

    def shiftTime(self, clock):
        for index, el in self.shift_parameters[self.hist_shift_index:].iterrows():
            if clock < el['range']:
                shift_parameter = el['lambda']
                break
        self.hist_shift_index = index
        return clock + expovariate(shift_parameter)

    def arrivalTime(self, clock):
        for index, el in self.arrival_parameters[self.hist_arrival_index:].iterrows():
            if clock < el['range']:
                arrival_parameter = el['lambda']
                break
        self.hist_arrival_index = index
        return clock+expovariate(arrival_parameter)

    def newDay(self):
        self.index_day += 1
        self.day = self.data.index[self.index_day]

    def fail_parameter(self):
        return self.fail_parameter

    def repair_parameter(self):
        return self.repair_parameter
