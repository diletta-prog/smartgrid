from random import expovariate


class Scheduler:
    def __init__(self, dati, shift_parameters, arrival_parameters, fail_parameter, repair_parameter):
        self.dati = dati
        self.shift_parameters = shift_parameters
        self.arrival_parameters = arrival_parameters
        self.fail_parameter = fail_parameter
        self.repair_parameter = repair_parameter
        self.hist_value_index = 0
        self.hist_shift_index = 0
        self.hist_arrival_index = 0
        self.index_day = 0
        self.day = 0    # giorni in secondi

    def checksuntime(self, clock):
        flag_day = False
        flag_suntime = True
        if clock >= (86400*(self.index_day+1)): # controllo se ho passato la mezzanotte
            self.newDay()
            flag_day = True
        sunrise = int(self.dati.at[self.index_day,'SUNRISE'])
        sunset = int(self.dati.at[self.index_day,'SUNSET'])
        if sunrise < clock and clock < sunset:
            flag_suntime = False
        return flag_suntime, flag_day

    def newDay(self):
        self.index_day += 1
        self.day = self.dati.at[self.index_day,'DATA']
        
        
        
    def shiftTime(self, clock):
        for index, el in self.shift_parameters[self.hist_shift_index:].iterrows():
            if clock < el['range']:
                shift_parameter = el['traffic']
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




    

    def fail_parameter(self):
        return self.fail_parameter

    def repair_parameter(self):
        return self.repair_parameter



    def lampValueCar(self, clock, fault):
        lamp_value = 0
        for index, el in self.dati[self.hist_value_index:].iterrows():
            if clock < el['DATA']:
                if fault == True:
                    lamp_value = el['FAILURE_TARGET_LUM']
                else:
                    lamp_value = el['TARGET_LUM']
                break
        self.hist_value_index = index
        return lamp_value

    def lampValueBase(self, clock, fault):
        lamp_value = 0
        for index, el in self.dati[self.hist_value_index:].iterrows(): # da controllare se possiamo lasciare hist_value_index 
            if clock < el['DATA']:
                if fault == True:
                    lamp_value = el['FAILURE_LUM_MIN']
                else:
                    lamp_value = el['MIN_LUM']
                break
        self.hist_value_index = index
        return lamp_value
