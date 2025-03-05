from cell_cycler import CellCycler
import time
import gmail

email = gmail.gmail()

cycler = CellCycler()
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_c_over_20_capacity_test.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-6436"
testname = 'PT-6436-C_over_20_capacity_test'

channels = [590203, 590204]

print("----P45B charge/discharge capacity test at C/20----")
ok_to_start = input(f"Test will start {len(channels)} channels in positions {channels}. Press 'y' to continue: ")
if ok_to_start != 'y':
    quit()

print("---starting capacity tests---")
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

print("---test complete---")
print("sending completion email")
email.send_email('ben.horst@flyzipline.com,erneste.niyigena@gmail.com', 'cell test complete', f'test {testname} on channels {channels} complete')