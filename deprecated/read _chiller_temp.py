from temperature_control import TemperatureController

controller = TemperatureController("COM5")
#controller.set_temperature(20)
print(controller.read_temperature())