
from temperature_control import TemperatureController

controller = TemperatureController("COm8")  # Replace "COM1" with the actual serial port
#controller.set_temperature(19.0)
#controller.wait_for_temperature(19.0)
#controller.read_temperature()
print("response is:",controller.set_temperature())
