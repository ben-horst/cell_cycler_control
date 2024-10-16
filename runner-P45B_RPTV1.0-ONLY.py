#runs only the P45B V1.0 RPT - to be used after cycle test - see SM-95

from cell_cycler import CellCycler
import time

cycler = CellCycler()
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.0.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/SM-95 - P45B V1.0 cycle test"

channels = [580201, 580202]

print("----runs only the P45B V1.0 RPT - to be used after cycle test - see SM-95----")
ok_to_start = input(f"Test will start {len(channels)} channels in positions {channels}. Press 'y' to continue: ")
if ok_to_start != 'y':
    quit()

cycle_number = input("enter cycle number: ")
rpt_testname = f'P45B_SM95_RPT_{cycle_number}'

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

print("pausing for 30 seconds before RPT")
time.sleep(30)

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