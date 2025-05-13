from core.temperature_control import TemperatureController

port = 'COM8'
temp = 28

chiller = TemperatureController(port)

chiller.set_temperature(temp)

#COM3 - 5901
#COM4 - 5801
#COM5 - 2701
#COM6 - 2702
#COM7 - 5201
#COM8 - 5202
