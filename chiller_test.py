from core.temperature_control import TemperatureController
import time

port = 'COM15'
temp = 35

chiller = TemperatureController(port)

chiller.set_temperature(temp)
print(chiller.read_temperature())

"""
2701 - COM13
2702 - COM9
5201 - COM14
5202 - COM12
5801 - COM11
5901 - COM15
5902 - COM10
"""