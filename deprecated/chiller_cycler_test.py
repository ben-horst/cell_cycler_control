from cell_cycler import CellCycler
from temperature_control import TemperatureController
import time

cycler = CellCycler()
chiller1 = TemperatureController("COM5")
profile = "C:/Users/cell.test/Documents/Unofficial Profiles/30s_rest_pause.xml"
savepath = "C:/Users/cell.test/Documents/BackupData"
testname = 'chiller_test'
channels = [270101]

#start by setting chamber to initial temp
temp = 23
print(f'setting initial temp: {temp}')
chiller1.set_temperature(temp)
chiller1.wait_for_temperature(temp, 0.5)
#once chiller reaches that temp, start test
print('temp achieved - starting test')
print(cycler.start_channels(channels, profile, savepath, testname))
#wait for all channels to complete
while not (cycler.all_channels_in_state(channels, 'pause')):
    print('waiting for channels to pause')
    time.sleep(5)
#start by setting chamber to next temp
temp = 22
print(f'setting next temp: {temp}')
chiller1.set_temperature(temp)
chiller1.wait_for_temperature(temp, 0.5)
#continue test once temp is reached
print('temp achieved - continuing test')
print(cycler.continue_channels(channels)) 
