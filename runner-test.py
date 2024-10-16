#runs only the P45B V1.0 RPT - to be used after cycle test - see SM-95

from cell_cycler import CellCycler
import time

cycler = CellCycler()
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/test_profile.xml"
savepath = "C:/Users/cell.test/Downloads/"
testname = 'test'

channels = [590108]

print("----basic test runner----")
ok_to_start = input(f"Test will start {len(channels)} channels in positions {channels}. Press 'y' to continue: ")
if ok_to_start != 'y':
    quit()

print("---starting RPT tests---")
start_data = cycler.start_channels(channels, rpt_profile, savepath, testname)

start_results = []
for item in start_data:
    start_results.append(item.get('start result'))
print(f'start result: {start_results}')

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