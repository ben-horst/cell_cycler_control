#runs the old P45B cycle test started by Bryan Hood and continued by Ben Horst - see SM-95

from cell_cycler import CellCycler
import time
import gmail

email = gmail.gmail()

cycler = CellCycler()
cycle_profile = "C:/Users/cell.test/Documents/Current Test Profiles/Cycle Tests/P45_cycle_test_V1.0.xml"
rpt_profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.0.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/SM-95 - P45B V1.0 cycle test"

cycle_number = input("enter cycle number: ")
run_RPT_only = ("SKIP" == input("press enter to start 100 cycles + RPT. To run RPT only, input 'SKIP': "))
cycle_testname = f'P45B_SM95_cycle_{cycle_number}'
rpt_testname = f'P45B_SM95_RPT_V1.0_cycle_{cycle_number}_35degC'
channels = [580201] #, 580202] - second channel removed 1/2/25 due to failed cell

if not run_RPT_only:
    cutoff_current = float(input("enter cutoff current (A): ")) * 1000  #in mA
    throughput_30soc = float(input("enter Ah for 30% SOC phase: "))
    throughput_0soc = float(input("enter Ah for 0% SOC (2.65 V) phase: "))


    #the next few lines will update the profile according to the values given from system modelling,
    #adjusting the depth of discharge for the cycle depending on the measured capacity from the prior cycle
    profile_params = {
        "current_cutoff_1": ["Step2", "Stop_Curr"],
        "current_cutoff_2": ["Step12", "Stop_Curr"],
        "current_cutoff_3": ["Step23", "Stop_Curr"],
        "Ah_throughput_30soc": ["Step8", "Cap"],
        "Ah_throughput_0soc": ["Step19", "Cap"]
    }

    new_params = {
        "current_cutoff_1": cutoff_current,    
        "current_cutoff_2": cutoff_current,   
        "current_cutoff_3": cutoff_current,   
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
print("sending completion email")
email_addresses = 'ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com,kyle.strohmaier@flyzipline.com'
completion_message = f'SM-95 P45B accumulation of cycle number {cycle_number} and RPT completed.'
email.send_email(email_addresses, 'Automated Cell Test Completion Notification', completion_message)