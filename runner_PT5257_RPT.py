#runs a multitemp water-cooled P30B and P45B cells, then charge/discharge to storage SOCs - see PT-5257

from core.test_runner import TestRunner

input("This script will run a multi-temp RPT for P30B and P45B cells, then charge to storage SOCs. Please ensure that 4 P45B cells are located in 580201-580204 and 4 P30B in 580205-580208.\n\nPress enter to continue")
cycle_number = input("enter number of aging days accumulated: ")
storage_temp = input("enter storage temperature for this group (0, 30, 60 C): ")

test_title = 'PT5257_RPTs'

#P30B cells
channels_P30 = [580205, 580206, 580207, 580208]
profile_RPT_P30 = "G:/My Drive/Cell Test Profiles/RPTs/P30_RPT_V1.1.xml"
charge_profile_base_P30 = "G:/My Drive/Cell Test Profiles/Utilities/calendar_storage/P30B_charge_to"
savepath_P30 = "G:/My Drive/Cell Test Data/PT5257/P30B"
testname_base_P30 = f'P30B_PT5257_day_{cycle_number}_RPT'

#P45B cells
channels_P45 = [580201, 580202, 580203, 580204]
profile_RPT_P45 = "G:/My Drive/Cell Test Profiles/RPTs/P45_RPT_V1.1.xml"
charge_profile_base_P45 = "G:/My Drive/Cell Test Profiles/Utilities/calendar_storage/P45B_charge_to"
savepath_P45 = "G:/My Drive/Cell Test Data/PT5257/P45B"
testname_base_P45 = f'P45B_day{cycle_number}_RPT'

#CQT settings
prchg_profile = "G:/My Drive/Cell Test Profiles/Utilities/storage_charge_P45B.xml"
cqt_profile_P30 = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P30B_1C_4C.xml"
cqt_profile_P45 = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5257/CQTs"
cqt_temp = 25

all_channels = channels_P30 + channels_P45

storage_socs = [0, 25, 50, 60, 70, 80, 90, 100]
temps = [20, 35, 50]

test_runner = TestRunner(all_channels, test_title)
barcodes = test_runner.barcodes

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
print('Charging cells before CQT.')
test_runner.start_tests(all_channels, prchg_profile, cqt_savepath, 'PRCHG')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60) 
print('Starting CQTs.')
test_runner.start_tests(channels_P30, cqt_profile_P30, cqt_savepath, 'CQT')
test_runner.start_tests(channels_P45, cqt_profile_P45, cqt_savepath, 'CQT')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

print('\nCQT successful!')

#THIS WON'T WORK BECAUSE WE'RE NOT DOING ALL 16 CELLS AT ONCE
#WE SHOULD BUILD A CONFIG FILE AND LOOK UP BY BARCODE

for temp in temps:
    print(f'Bringing cells to {temp} degC for RPT')
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60)
    print('starting P30 RPTs')
    filenames_P30 = []
    for soc, channel in zip(storage_socs, channels_P30):
        filenames_P30.append(f'{testname_base_P30}_at_{temp}degC-stored_at_{soc}soc_{storage_temp}degC')
    test_runner.start_tests(channels_P30, profile_RPT_P30, savepath_P30, filenames_P30)
    print('starting P45 RPTs')
    filenames_P45 = []
    for soc, channel in zip(storage_socs, channels_P45):
        filenames_P45.append(f'{testname_base_P45}_at_{temp}degC-stored_at_{soc}soc_{storage_temp}degC')
       

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