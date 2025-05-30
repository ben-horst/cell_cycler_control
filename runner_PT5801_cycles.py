import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager
from core.progress_report_PT5801 import ProgressReporter
import os

profile_parent_folder = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_tuned_profiles"
savepath = "G:/My Drive/Cell Test Data/PT5801/Cycles"
test_title = 'PT5801_Cycles'

cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 25
cqt_filenames = []

strg_profile = "G:/My Drive/Cell Test Profiles/Utilities/storage_charge_P45B.xml"
strg_savepath = "G:/My Drive/Cell Test Data/PT5801/Storage_Charges"
strg_temp = 20
strg_filename = 'storage_charge'

# Find the most recently modified folder within the parent folder
folders = [os.path.join(profile_parent_folder, d) for d in os.listdir(profile_parent_folder) if os.path.isdir(os.path.join(profile_parent_folder, d))]
if not folders:
    raise ValueError("No folders found in the parent folder.")
profile_folder = max(folders, key=os.path.getmtime)
print(f"Folder for profiles: {profile_folder}")

#prompt user for which bank to run
#TODO: add the ability to run multiple banks from one script, for now only one bank at a time
bank_request = int(input('Enter the bank to run (only one bank at a time for now): '))

if bank_request not in CONFIG.AVAILABLE_BANKS:
    raise ValueError(f"Invalid bank number. Available banks are {CONFIG.AVAILABLE_BANKS}.")

#add all channels and specimens into big lists
channels = CONFIG.CHANNELS_PER_BANK[bank_request]
specimens = CONFIG.SPECIMENS_PER_BANK[bank_request]
print(f'All specimens in bank {bank_request}: {specimens}')

#ask user for the specimens to skip, if any
specimens_to_skip = input("Enter the specimens to skip, separated by commas, or press enter to skip no specimens: ")
if specimens_to_skip:
    specimens_to_skip = [specimen.strip() for specimen in specimens_to_skip.split(',')]
    channels_to_skip = [channels[specimens.index(specimen)] for specimen in specimens_to_skip if specimen in specimens]
    print(f'specimens to skip: {specimens_to_skip} on channels: {channels_to_skip}')
    #remove the specimens to skip from the list of specimens and channels
    specimens = [specimen for specimen in specimens if specimen not in specimens_to_skip]
    channels = [channel for channel in channels if channel not in channels_to_skip]

cycle_manager = CycleManager()
print(f'\nSpecimen cycle counts from cycle tracker json file for bank {bank_request}:')
print('---------------------------------------------------------------')
print('Specimen ID:\tlast cycle number\tlast cycle direction')

#for each specimen, lookup the cycle number and direction from the cycle tracker json file
for specimen in specimens:
    #lookup cycle number for each specimen
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    cqt_filenames.append(f'{specimen}_CQT_after_{cycle}_cycles')
    print(f'{specimen}\t\t\t{cycle}\t\t\t{direction}')

#check that all the profiles for these specimens exist in the selected folder
suffixes = ['FC', 'SC', 'EX', 'ST']
for specimen in specimens:
    for suffix in suffixes:
        profile_name = f'{specimen}_{suffix}.xml'
        profile_path = f'{profile_folder}/{profile_name}'
        if not os.path.isfile(profile_path):
            raise ValueError(f"Profile {profile_name} not found in {profile_folder}.")
print('\nAll profiles found for all specimens!\n')

cycles_to_complete = int(input('Enter the number of cycles to complete: '))
if cycles_to_complete <= 0:
    raise ValueError("Invalid number of cycles. Must be greater than 0.")

print('')

test_runner = TestRunner(channels, test_title)
barcodes = test_runner.barcodes

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30, verbose=False)
#make sure nothing is running
print('Waiting for any tests to complete')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60, verbose=False)  
test_runner.start_tests(channels, cqt_profile, cqt_savepath, cqt_filenames, verbose=False)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4, verbose=False)  
for specimen in specimens:
   cycle_manager.update_cycle_tracker(specimen, 'CQT', increment=False)  #update cycle tracker
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits
print('\nCQT successful! Bringing cells to target charge temp...')

cycles_completed = 0

while cycles_completed < cycles_to_complete:
    #set bank to charge temp and wait
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=CONFIG.BANK_CHARGE_TEMPS[bank_request], timeout_mins=60, verbose=False)

    #charge all cells
    print(f'Starting charge {cycles_completed+1}/{cycles_to_complete} on bank {bank_request}...')
    print('---------------------------------------------------------------')
    print('Specimen ID:\tChannel ID\tCycle\tCharge Type\tStart Result')
    for specimen in specimens:
        last_cycle, direction = cycle_manager.get_last_cycle(specimen)       #checks to see the last cycle
        current_cycle = last_cycle + 1              #lookup table only tracks completed cycles, so the current cycle is incremented
        charge_type = cycle_manager.get_charge_type(current_cycle, specimen)    #pulls from the cycle lookup table to see if it is a fast or slow charge
        charge_profile = f'{specimen}_{charge_type}.xml'
        charge_profile_path = f'{profile_folder}/{charge_profile}'       #builds the path to the charge profile
        channel = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]  #finds the channel for the specimen
        charge_filename = f'{specimen}_cycle_{current_cycle}_chg'
        result = test_runner.start_tests([channel], charge_profile_path, savepath, charge_filename, verbose=False)   #starts the charge tests
        print(f'{specimen}\t\t{channel}\t\t{current_cycle}\t{charge_type}\t\t{result[0]}')
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=300, verbose=False)
    print(f'Charge event {cycles_completed+1}/{cycles_to_complete} complete for all specimens in bank {bank_request}')
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, 'CHG', increment=False)  #update cycle tracker - INCREMENTS ONLY AT THE DISCHARGE EVENT

    # set bank to discharge temp and wait
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=CONFIG.DISCHARGE_TEMP, timeout_mins=60, verbose=False)

    #discharge all cells
    print(f'Starting discharge {cycles_completed+1}/{cycles_to_complete} on bank {bank_request}...')
    print('---------------------------------------------------------------')
    print('Specimen ID:\tChannel ID\tCycle\tDischarge Type\tStart Result')
    for specimen in specimens:
        last_cycle, direction = cycle_manager.get_last_cycle(specimen)       #checks to see the last cycle
        current_cycle = last_cycle + 1 
        discharge_type = cycle_manager.get_discharge_type(current_cycle, specimen)    #pulls from the cycle lookup table to see if it is a fast or slow charge
        discharge_profile = f'{specimen}_{discharge_type}.xml'
        discharge_profile_path = f'{profile_folder}/{discharge_profile}'       #builds the path to the charge profile
        channel = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]  #finds the channel for the specimen
        discharge_filename = f'{specimen}_cycle_{current_cycle}_dchg'
        result = test_runner.start_tests([channel], discharge_profile_path, savepath, discharge_filename, verbose=False)   #starts the charge tests
        print(f'{specimen}\t\t{channel}\t\t{current_cycle}\t{discharge_type}\t\t{result[0]}')
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=120, verbose=False)
    print(f'Discharge event {cycles_completed+1}/{cycles_to_complete} complete for all specimens in bank {bank_request}')
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, 'DCHG', increment=True)  #update cycle tracker - INCREMENTS ONLY AT THE DISCHARGE EVENT
    #increment cycle counter and repeat
    cycles_completed += 1
    print(f'Completed {cycles_completed} cycles out of {cycles_to_complete} on bank {bank_request}')

print('All cycles complete!')
#perform storage charge
print('Setting temperature for storage charge...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=strg_temp, timeout_mins=30, verbose=False)
test_runner.start_tests(channels, strg_profile, strg_savepath, strg_filename, verbose=False)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=120, verbose=False)  
for specimen in specimens:
   cycle_manager.update_cycle_tracker(specimen, 'STRG', increment=False)  #update cycle tracker
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits
print('\nStorage Charge Complete.\n')

print('\nSpecimen status after tests.\n')
print('---------------------------------------------------------------')
summary_table = 'Specimen\tBarcode\t\tChannel\t\tLast Cycle\tLast Event\n'
for specimen in specimens:
    last_cycle, last_event = cycle_manager.get_last_cycle(specimen)       #checks to see the last cycle
    chan = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]  #finds the channel for the specimen
    barcode = barcodes[specimens.index(specimen)]
    summary_table += f'{specimen}\t\t{barcode}\t{chan}\t\t{last_cycle}\t\t{last_event}\n'

print(summary_table)

#generate csv progress report and save copy of json tracker file
progress_reporter = ProgressReporter()
progress_reporter.generate_progress_report_csv()
progress_reporter.save_copy_cycle_tracker_json()

message = f'''{cycles_to_complete} cycles completed successfully for cycle accumulation of PT-5801. All data saved to {savepath}.
                       \n\nBank tested: {bank_request}
                       \n\nSpecimens tested: {specimens}
                       \n\nCells Tested: {barcodes}
                       \n\n{summary_table}'''

test_runner.send_email(f'{test_title} Complete', message)

print('Test complete. Exiting.')