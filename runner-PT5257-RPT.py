#runs a multitemp water-cooled P30B and P45B cells, then charge/discharge to storage SOCs - see PT-5257

from cell_cycler import CellCycler
from temperature_control import TemperatureController
import time
import sys

cell_type = input("enter cell type (P30B, P45B): ")
cycle_number = input("enter number of aging days accumulated: ")

if cell_type == 'P30B':
    channels = [580101, 580102, 580103, 580104, 580105, 580106, 580107, 580108]
    #profile_RPT = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P30_RPT_V1.1.xml"
    profile_RPT = "C:/Users/cell.test/Documents/Unofficial Profiles/30s_rest.xml"
    charge_profile_base = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/P30B_charge_to"
    savepath = "C:/Users/cell.test/Documents/Test Data/PT-5257/P30B"
    testname_base = f'P30B_RPT_day{cycle_number}'
    chiller = TemperatureController("COM5")
elif cell_type == 'P45B':
    channels = [270101, 270102, 270103, 270104, 270105, 270106, 270107, 270108]
    #profile_RPT = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.1.xml"
    profile_RPT = "C:/Users/cell.test/Documents/Unofficial Profiles/30s_rest.xml"
    charge_profile_base = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/P45B_charge_to"
    savepath = "C:/Users/cell.test/Documents/Test Data/PT-5257/P45B"
    testname_base = f'P45B_RPT_day{cycle_number}'
    chiller = TemperatureController("COM3")
else:
    print('invalid cell type')
    sys.exit()

storage_socs = [0, 25, 50, 60, 70, 80, 90, 100]
cycler = CellCycler()
temps = [20, 35, 50]
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

    start_results = []

    for soc, channel in zip(storage_socs, channels):
        testname = f'{testname_base}_{temp}degC_SOC{soc}'
        start_data = cycler.start_channels([channel], profile_RPT, savepath, testname)
        for item in start_data:
            start_results.append(item.get('start result'))
  
    
    print(f'start result at {temp}deg C: {start_results}')
    
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

print('test completed - setting chiller to 20 C and charging cells to storage SOCs')
chiller.set_temperature(20)
time.sleep(30)

charge_start_results = []
for soc, channel in zip(storage_socs, channels):
    charge_testname = f'{testname_base}_charge_to_{soc}soc'
    charge_profile = f"{charge_profile_base}_{soc}SOC.xml"
    charge_savepath = savepath + '/charges'
    start_data = cycler.start_channels([channel], charge_profile, charge_savepath, charge_testname)
    for item in start_data:
        charge_start_results.append(item.get('start result'))

print(f'charge start results: {charge_start_results}')
