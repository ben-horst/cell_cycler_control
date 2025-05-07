from core.temperature_control import TemperatureController

class ChillerController():
    #def __init__(self, banks, comports={2701:"COM6", 2702:"COM7", 5201:"COM9", 5202:"COM8", 5801:"COM5", 5802:"COM4", 5901:"COM3"}):
    def __init__(self, banks, comports={2701:"COM8", 2702:"COM5", 5201:"COM7", 5202:"COM4", 5801:"COM3", 5802:"COM", 5901:"COM6"}):
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
