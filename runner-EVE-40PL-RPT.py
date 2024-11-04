#runs only the P45B V1.0 RPT - to be used after cycle test - see SM-95

from cell_cycler import CellCycler
import time
import gmail

email = gmail.gmail()

cycler = CellCycler()
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/40PL_RPT_V1.1.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-5698 - 40PL RPT"
testname = '40PL_RPT_35degC'

channels = [590105, 590106]

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

print("---test complete---")
print("sending completion email")
email_addresses = 'ben.horst@flyzipline.com'
completion_message = f'PT-5698 EVE 40PL Initial RPT Test complete on channels {channels}.'
email.send_email(email_addresses, 'Automated Cell Test Completion Notification', completion_message)