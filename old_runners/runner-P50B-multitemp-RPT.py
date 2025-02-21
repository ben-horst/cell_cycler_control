from cell_cycler import CellCycler
from chiller_controller import ChillerController
import time
import sys

cycler = CellCycler()
chillers = ChillerController()

chiller_num = 2
#temps = [20, 35, 50]
temps = [34]
temp_padding = 0
channels_v10 = [590101, 590102]
channels_v11 = [590103, 590104]
all_channels = channels_v10 + channels_v11

#profile_RPT_v10 = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/test_profile.xml"
#profile_RPT_v11 = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/test_profile.xml"
profile_RPT_v10 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P50_RPT_V1.0.xml"
profile_RPT_v11 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P50_RPT_V1.1.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT4824 - P50B Cycle Test"
cycle_number = input("enter cycle number: ")

for temp in temps:
    temp_padding = 0
    chiller_target = temp
    print(f'setting chiller to {chiller_target}degC')
    chillers.set_temp(chiller_num, chiller_target)
    #wait for chiller to reach temp
    while True:
        chiller_temp = chillers.read_temp(chiller_num)
        chan_data = cycler.get_channels_current_data(all_channels)
        cell_temps = []
        for chan in chan_data:
            cell_temps.append(float(chan.get('auxtemp')))
        min_cell_temp = min(cell_temps)
        max_cell_temp = max(cell_temps)
        print(f'chiller temp: {chiller_temp}  |  min cell temp: {min_cell_temp}  |  max cell temp: {max_cell_temp}')
        
        if abs(temp - min_cell_temp) < 2 and abs(temp - max_cell_temp) < 2:
            print(f'cell target temp reached: {min_cell_temp}degC')
            break
        elif abs(chiller_target - chiller_temp)  < 1:     #if the cell temp isn't reached, but the chiller temp has, then increase the chiller temp - needed due to heat loss to ambient
            temp_padding = temp_padding + 1
            chiller_target = temp + temp_padding
            print(f'setting chiller to {chiller_target}degC')
            chillers.set_temp(chiller_num, chiller_target)
        time.sleep(30)
    
    print('starting RPTs')
    testname_v10 = f'P50B_RPT_V1.0_cycle_{cycle_number}_{temp}degC'
    testname_v11 = f'P50B_RPT_V1.1_cycle_{cycle_number}_{temp}degC'
    start_data_v10 = cycler.start_channels(channels_v10, profile_RPT_v10, savepath, testname_v10)
    start_data_v11 = cycler.start_channels(channels_v11, profile_RPT_v11, savepath, testname_v11)
    start_results_v10 = []
    start_results_v11 = []
    for item in start_data_v10:
        start_results_v10.append(item.get('start result'))
    for item in start_data_v11:
        start_results_v11.append(item.get('start result'))
    print(f'RPT V1.0 start result at {temp}deg C: {start_results_v10}')
    print(f'RPT V1.1 start result at {temp}deg C: {start_results_v11}')
    time.sleep(30)
    while True:
        chan_data = cycler.get_channels_current_data(all_channels)
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

print('test completed - setting chiller to 20 C')
chillers.set_temp(chiller_num, 20)