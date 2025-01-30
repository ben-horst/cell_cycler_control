from temperature_control import TemperatureController

class ChillerController():
    def __init__(self, comports={2701:"COM6", 2702:"COM7", 5201:"COM9", 5202:"COM8", 5801:"COM5", 5802:"COM4", 5901:"COM3"}):
        self.chillers = {}  #dictionary containing objects for the chillers
        for num, port in comports.items():
            self.chillers.update({num: TemperatureController(port)})
    
    def set_temp(self, bank, temp):
        if bank not in self.chillers:
            return "Invalid bank number"
        else:
            return self.chillers[bank].set_temperature(temp)
    
    def read_temp(self, bank):
        if bank not in self.chillers:
            return "Invalid bank number"
        else:
            return self.chillers[bank].read_temperature()
