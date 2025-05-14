#runs a multitemp water-cooled P30B and P45B cells, then charge/discharge to storage SOCs - see PT-5257

from core.cell_cycler import CellCycler
from core.chiller_controller import ChillerController
from core.gmail import gmail
import time

email = gmail.gmail()

input("This script will run a multi-temp RPT for P30B and P45B cells, then charge to storage SOCs. Please ensure that cells are properly located in banks 2701 and 5801. Press enter to continue")
cycle_number = input("enter number of aging days accumulated: ")
storage_temp = input("enter storage temperature for this group (0, 30, 60 C): ")

#P30B cells
channels_P30 = [270105, 270106, 270107, 270108, 580105, 580106, 580107, 580108]
profile_RPT_P30 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P30_RPT_V1.1.xml"
charge_profile_base_P30 = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/P30B_charge_to"
savepath_P30 = "C:/Users/cell.test/Documents/Test Data/PT-5257/P30B"
testname_base_P30 = f'P30B_PT5257_day_{cycle_number}_RPT'

#P45B cells
channels_P45 = [270101, 270102, 270103, 270104, 580101, 580102, 580103, 580104]
profile_RPT_P45 = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.1.xml"
charge_profile_base_P45 = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/P45B_charge_to"
savepath_P45 = "C:/Users/cell.test/Documents/Test Data/PT-5257/P45B"
testname_base_P45 = f'P45B_day{cycle_number}_RPT'

banks = [2701, 5801]
chiller_controller = ChillerController(banks)
all_channels = channels_P30 + channels_P45
bank_channels = {}
for bank in banks:
    channels_in_bank = []
    for i in range(1, 9):
        channels_in_bank.append(bank * 100 + i)
    bank_channels.update({bank: channels_in_bank})

storage_socs = [0, 25, 50, 60, 70, 80, 90, 100]
cycler = CellCycler()
temps = [20, 35, 50]

for temp in temps:
    temp_paddings = dict.fromkeys(banks, 0)
    chiller_targets = dict.fromkeys(banks, temp)
    temps_ok = dict.fromkeys(banks, False)
    for bank in banks:
        chiller_controller.set_temp(bank, chiller_targets[bank])
        print(f'chiller for {bank} set to {chiller_targets[bank]}degC')
    #wait for chillers to reach temp
    while True:
        if all(temps_ok.values()):
            print('all chillers reached target temperature')
            break
        for bank in banks:
            if not temps_ok[bank]:
                chiller_temp = chiller_controller.read_temp(bank)
                chan_data = cycler.get_channels_current_data(bank_channels[bank])
                cell_temps = []
                for chan in chan_data:
                    cell_temps.append(float(chan.get('auxtemp')))
                min_cell_temp = min(cell_temps)
                max_cell_temp = max(cell_temps)
                print(f'bank {bank} -- chiller temp: {chiller_temp}  |  min cell temp: {min_cell_temp}  |  max cell temp: {max_cell_temp}')
            
                if abs(temp - min_cell_temp) < 5 and abs(temp - max_cell_temp) < 5:
                    print(f'bank {bank} cell target temp reached: {min_cell_temp}degC')
                    temps_ok[bank] = True
                elif abs(chiller_targets[bank] - chiller_temp)  < 1:     #if the cell temp isn't reached, but the chiller temp has, then increase the chiller temp - needed due to heat loss to ambient
                    avg_cell_temp = (min_cell_temp + max_cell_temp) / 2
                    if avg_cell_temp < temp:
                        temp_paddings[bank] = temp_paddings[bank] + 1
                    elif avg_cell_temp > temp:
                        temp_paddings[bank] = temp_paddings[bank] - 1
                    chiller_targets[bank] = temp + temp_paddings[bank]
                    print(f'setting chiller to {chiller_targets[bank]}degC')
                    chiller_controller.set_temp(bank, chiller_targets[bank])
        time.sleep(30)
    
    print('starting P30 RPTs')
    start_results_P30 = []
    for soc, channel in zip(storage_socs, channels_P30):
        testname = f'{testname_base_P30}_at_{temp}degC-stored_at_{soc}soc_{storage_temp}degC'
        start_data = cycler.start_channels([channel], profile_RPT_P30, savepath_P30, testname)
        for item in start_data:
            start_results_P30.append(item.get('start result'))
        time.sleep(0.25)
    print(f'P30 start result at {temp}deg C: {start_results_P30}')

    time.sleep(5)

    print('starting P45 RPTs')
    start_results_P45 = []
    for soc, channel in zip(storage_socs, channels_P45):
        testname = f'{testname_base_P45}_at_{temp}degC-stored_at_{soc}soc_{storage_temp}degC'
        start_data = cycler.start_channels([channel], profile_RPT_P45, savepath_P45, testname)
        for item in start_data:
            start_results_P45.append(item.get('start result'))
        time.sleep(0.25)
    print(f'P45 start result at {temp}deg C: {start_results_P45}')
    
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

print('all RPTs completed - setting chiller to 20 C and charging cells to storage SOCs')
for bank in banks:
    chiller_controller.set_temp(bank, 20)
time.sleep(30)

charge_start_results_P30 = []
for soc, channel in zip(storage_socs, channels_P30):
    charge_testname = f'{testname_base_P30}_charge_to_{soc}soc'
    charge_profile = f"{charge_profile_base_P30}_{soc}SOC.xml"
    charge_savepath = savepath_P30 + '/charges'
    start_data = cycler.start_channels([channel], charge_profile, charge_savepath, charge_testname)
    for item in start_data:
        charge_start_results_P30.append(item.get('start result'))
    time.sleep(0.25)
print(f'P30 charge start results: {charge_start_results_P30}')

time.sleep(5)

charge_start_results_P45 = []
for soc, channel in zip(storage_socs, channels_P45):
    charge_testname = f'{testname_base_P45}_charge_to_{soc}soc'
    charge_profile = f"{charge_profile_base_P45}_{soc}SOC.xml"
    charge_savepath = savepath_P45 + '/charges'
    start_data = cycler.start_channels([channel], charge_profile, charge_savepath, charge_testname)
    for item in start_data:
        charge_start_results_P45.append(item.get('start result'))
    time.sleep(0.25)
print(f'P45 charge start results: {charge_start_results_P45}')

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

print("---test complete---")
print("sending completion email")
email_addresses = 'ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com'
completion_message = f'PT-5257 calendar aging multi-temp RPT completed for cells stored at {storage_temp} degC for {cycle_number} days. Cells tested are in channels {all_channels}. Please return cells to aging chamber and start next test.'
email.send_email(email_addresses, 'Automated Cell Test Completion Notification', completion_message)