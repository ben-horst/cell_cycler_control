from temperature_control import TemperatureController

class ChillerController():
    def __init__(self, comports={1:"COM5", 2:"COM3"}):
        self.chillers = {}  #dictionary containing objects for the chillers
        for num, port in comports.items():
            self.chillers.update({num: TemperatureController(port)})
    
    def set_temp(self, chiller, temp):
        return self.chillers[chiller].set_temperature(temp)
    
    def read_temp(self, chiller):
        return self.chillers[chiller].read_temperature()