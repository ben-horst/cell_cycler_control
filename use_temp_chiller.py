from temperature_control import TemperatureController

controller = TemperatureController("COM8")  # Replace "COM1" with the actual serial port
print("Current temperature:", controller.set_temperature(22))
#controller.set_temperature(19.0)
controller.wait_for_temperature(21.5)
print("tempetaruture set at :", controller.read_temperature())
