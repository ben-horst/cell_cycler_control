from core.temperature_control import TemperatureController

class ChillerController():
    def __init__(self, banks, comports={2701:"COM13", 2702:"COM9", 5201:"COM14", 5202:"COM12", 5801:"COM11", 5802:"COM", 5901:"COM15", 5902:"COM10"}):
        #initialize with list of banks that should be controlled
        self.chillers = {}  #dictionary containing objects for the chillers
        for bank in banks:
            if bank not in comports.keys():
                return f"Bank {bank} does not have associated comport"
            else:
                self.chillers.update({bank: TemperatureController(comports.get(bank))})
    
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
