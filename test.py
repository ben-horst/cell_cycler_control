from temperature_control import TemperatureController

chiller = TemperatureController('COM8')

print(chiller.read_temperature())