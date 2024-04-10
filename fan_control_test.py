from cell_cycler import CellCycler
from fan_control import FanController

cycler = CellCycler()
fan = FanController('COM4')
relay_num = 0
profile = "C:/Users/cell.test/Documents/Unofficial Profiles/30s_rest_pause.xml"
savepath = "C:/Users/cell.test/Documents/BackupData"
testname = 'fan_test'
channels = [270101]

#start fans off
fan.turn_off(0)
print(f'fan state: {fan.get_relay_state(0)}')

#start a test that includes both charge and discharge steps
print(cycler.start_channels(channels, profile, savepath, testname))
while(True):
    if cycler.all_channels_in_state(channels, 'finish'):
        fan.turn_off(relay_num)
        break   #exit loop once all channels are done
    if cycler.all_channels_in_state(channels, 'working'):
        all_discharging = (cycler.all_channels_in_step(channels, 'dc') or cycler.all_channels_in_step(channels, 'dp'))
        all_charging = (cycler.all_channels_in_step(channels, 'cc') or cycler.all_channels_in_step(channels, 'cp'))
        if all_charging:
            fan.turn_on(relay_num)
        elif all_discharging:
            fan.turn_off(relay_num)
    
