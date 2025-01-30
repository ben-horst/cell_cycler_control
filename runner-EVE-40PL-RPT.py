#See PT-5698

from cell_cycler import CellCycler
from temperature_control import TemperatureController
import time
import gmail

email = gmail.gmail()

cycler = CellCycler()
chiller = TemperatureController("COM3")
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/40PL_RPT_V1.1.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-5698 - 40PL RPT"
testname = '40PL_PT5698_RPT_35degC'


channels = [590105, 590106]

print("----PT-5698 test runner----")
ok_to_start = input(f"Test will start {len(channels)} channels in positions {channels}. Press 'y' to continue: ")
if ok_to_start != 'y':
    quit()

temps = [35]
temp_padding = 0

for temp in temps:
    temp_padding = 0
    chiller_target = temp
    print(f'setting chiller to {chiller_target}degC')
    chiller.set_temperature(chiller_target)
    #wait for chiller to reach temp
    while True:
        chiller_temp = chiller.read_temperature()
        chan_data = cycler.get_channels_current_data(channels)
        cell_temps = []
        for chan in chan_data:
            cell_temps.append(float(chan.get('auxtemp')))
        min_cell_temp = min(cell_temps)
        max_cell_temp = max(cell_temps)
        print(f'chiller temp: {chiller_temp}  |  min cell temp: {min_cell_temp}  |  max cell temp: {max_cell_temp}')
        
        if abs(temp - min_cell_temp) < 5 and abs(temp - max_cell_temp) < 5:
            print(f'cell target temp reached: {min_cell_temp}degC')
            break
        elif abs(chiller_target - chiller_temp)  < 1:     #if the cell temp isn't reached, but the chiller temp has, then increase the chiller temp - needed due to heat loss to ambient
            avg_cell_temp = (min_cell_temp + max_cell_temp) / 2
            if avg_cell_temp < temp:
                temp_padding = temp_padding + 1
            elif avg_cell_temp > temp:
                temp_padding = temp_padding - 1
            chiller_target = temp + temp_padding
            print(f'setting chiller to {chiller_target}degC')
            chiller.set_temperature(chiller_target)
        time.sleep(30)
    
    print('starting RPTs')

print("---starting RPT tests---")
start_data = cycler.start_channels(channels, rpt_profile, savepath, testname)

start_results = []
for item in start_data:
    start_results.append(item.get('start result'))
print(f'start result: {start_results}')

time.sleep(30)

while True:
    chan_data = cycler.get_channels_current_data(channels)
    cell_states = []
    cell_temps = []
    for chan in chan_data:
        cell_states.append(chan.get('workstatus'))
        cell_temps.append(float(chan.get('auxtemp')))
    print(f'channel states: {cell_states}  |  channel temps: {cell_temps}')
    if all(state == 'finish' for state in cell_states):
        print('all channels finished')
        break
    else:
        time.sleep(30)

print("---test complete---")
print("sending completion email")
email_addresses = 'ben.horst@flyzipline.com'
completion_message = f'PT-5698 EVE 40PL Initial RPT Test complete on channels {channels}.'
email.send_email(email_addresses, 'Automated Cell Test Completion Notification', completion_message)