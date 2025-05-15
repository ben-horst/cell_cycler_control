from core.temperature_control import TemperatureController
import time

port = 'COM8'
temp = 24

chiller = TemperatureController(port)

chiller.set_temperature(temp)
print(chiller.read_temperature())

#COM3 - 5901
#COM4 - 5801
#COM5 - 2701
#COM6 - 2702
#COM7 - 5201
#COM8 - 5202
