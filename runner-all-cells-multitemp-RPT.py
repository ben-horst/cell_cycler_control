#runs a multitemp water-cooled RPT on 2 each of all 4 cells - see PT-4863

from cell_cycler import CellCycler
from temperature_control import TemperatureController
import time
import sys

cycler = CellCycler()
chiller = TemperatureController("COM5")

#chiller_num = 1
temps = [50]
temp_padding = 0
channels_p45 = [580101, 580102]
channels_p50 = [580103, 580104]
channels_p30 = [580105, 580106]
channels_p28 = [580107, 580108]
all_channels = channels_p45 + channels_p50 + channels_p30 + channels_p28

profile_RPT_p45 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.1.xml"
profile_RPT_p50 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P50_RPT_V1.1.xml"
profile_RPT_p30 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P30_RPT_V1.1.xml"
profile_RPT_p28 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P28_RPT_V1.1.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-4863 - all cells RPT"
cycle_number = input("enter cycle number: ")

for temp in temps:
    temp_padding = 0
    chiller_target = temp
    print(f'setting chiller to {chiller_target}degC')
    chiller.set_temperature(chiller_target)
    #wait for chiller to reach temp
    while True:
        chiller_temp = chiller.read_temperature()
        chan_data = cycler.get_channels_current_data(all_channels)
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
    testname_p45 = f'P45B_RPT_V1.1_cycle_{cycle_number}_{temp}degC'
    testname_p50 = f'P50B_RPT_V1.1_cycle_{cycle_number}_{temp}degC'
    testname_p30 = f'P30B_RPT_V1.1_cycle_{cycle_number}_{temp}degC'
    testname_p28 = f'P28A_RPT_V1.1_cycle_{cycle_number}_{temp}degC'
    
    start_data_p45 = cycler.start_channels(channels_p45, profile_RPT_p45, savepath, testname_p45)
    start_data_p50 = cycler.start_channels(channels_p50, profile_RPT_p50, savepath, testname_p50)
    start_data_p30 = cycler.start_channels(channels_p30, profile_RPT_p30, savepath, testname_p30)
    start_data_p28 = cycler.start_channels(channels_p28, profile_RPT_p28, savepath, testname_p28)
    
    start_results_p45 = []
    start_results_p50 = []
    start_results_p30 = []
    start_results_p28 = []

    for item in start_data_p45:
        start_results_p45.append(item.get('start result'))
    for item in start_data_p50:
        start_results_p50.append(item.get('start result'))
    for item in start_data_p30:
        start_results_p30.append(item.get('start result'))
    for item in start_data_p28:
        start_results_p28.append(item.get('start result'))
    
    print(f'P45B start result at {temp}deg C: {start_results_p45}')
    print(f'P50B start result at {temp}deg C: {start_results_p50}')
    print(f'P30B start result at {temp}deg C: {start_results_p30}')
    print(f'P28A start result at {temp}deg C: {start_results_p28}')
    
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
chiller.set_temperature(20)