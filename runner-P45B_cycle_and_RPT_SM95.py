#runs the old P45B cycle test started by Bryan Hood and continued by Ben Horst - see SM-95

from cell_cycler import CellCycler
import time

cycler = CellCycler()
cycle_profile = "C:/Users/cell.test/Documents/Current Test Profiles/Cycle Tests/P45_cycle_test_V1.0.xml"
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.0.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/SM-95 - P45B V1.0 cycle test"

cycle_number = input("enter cycle number: ")
throughput_30soc = float(input("enter Ah for 30% SOC phase: "))
throughput_0soc = float(input("enter Ah for 0% SOC (2.65 V) phase: "))
cycle_testname = f'P45B_SM95_cycle_{cycle_number}'
rpt_testname = f'P45B_SM95_RPT_{cycle_number}'

channels = [580201, 580202]


#the next few lines will update the profile according to the values given from system modelling,
#adjusting the depth of discharge for the cycle depending on the measured capacity from the prior cycle
profile_params = {
    "Ah_throughput_30soc": ["Step8", "Cap"],
    "Ah_throughput_0soc": ["Step19", "Cap"]
}

new_params = {
    "Ah_throughput_30soc": throughput_30soc,
    "Ah_throughput_0soc": throughput_0soc
}

cycler.update_test_profile_params(cycle_profile, profile_params, new_params)

print("---starting cycle tests---")
start_data = cycler.start_channels(channels, cycle_profile, savepath, cycle_testname)

start_results = []
for item in start_data:
    start_results.append(item.get('start result'))
print(f'P45B cycle test #{cycle_number} start result: {start_results}')

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

print("pausing for 30 minutes before RPT")
time.sleep(1800)

print("---starting RPT tests---")
start_data = cycler.start_channels(channels, rpt_profile, savepath, rpt_testname)

start_results = []
for item in start_data:
    start_results.append(item.get('start result'))
print(f'P45B RPT test #{cycle_number} start result: {start_results}')

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

print(f'cycle and RPT #{cycle_number} complete')