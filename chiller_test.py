from chiller_controller import ChillerController
import time


chiller_controller = ChillerController()

# set the temperature of bank 5801 to 27 degrees
print(chiller_controller.set_temp(5801, 27))
while True:
    # read the temperature of bank 5801
    print(chiller_controller.read_temp(5801))
    time.sleep(5)
