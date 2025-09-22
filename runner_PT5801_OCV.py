import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager
from core.progress_report_PT5801 import ProgressReporter
import os

profile_parent_folder = "G:/My Drive/Cell Test Profiles/RPTs/PT5801_tuned_OCV_profiles"
savepath = "G:/My Drive/Cell Test Data/PT5801/OCVs"
temp = 25
test_title = 'PT5801_OCVs'

cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 25

ack = input('This will perform OCV extraction. Confirm that prior to running this test, profile_editor_PT5801.py was run to generate new OCV profiles. Type YES to acknowledge:  ')
if ack != 'YES':
    raise ValueError('Please run profile editor and try again.')

# Find the most recently modified folder within the parent folder
folders = [os.path.join(profile_parent_folder, d) for d in os.listdir(profile_parent_folder) if os.path.isdir(os.path.join(profile_parent_folder, d))]
if not folders:
    raise ValueError("No folders found in the parent folder.")
profile_folder = max(folders, key=os.path.getmtime)
print(f"Folder for chg/dchg OCV profiles: {profile_folder}")

bank_request = input("Enter the banks for OCV extraction execution, separated by commas, or enter 'ALL' to use all 6 banks: ")
if bank_request == 'ALL':
    active_banks = CONFIG.AVAILABLE_BANKS
else:
    active_banks = [int(bank.strip()) for bank in bank_request.split(',')]
if not all([bank in CONFIG.AVAILABLE_BANKS for bank in active_banks]):
    raise ValueError(f"Invalid bank number. Available banks are {CONFIG.AVAILABLE_BANKS}.")

#add all channels and specimens into big lists
channels = []
specimens = []
for bank in active_banks:
    channels.extend(CONFIG.CHANNELS_PER_BANK[bank])
    specimens.extend(CONFIG.SPECIMENS_PER_BANK[bank])

print(f'All specimens in banks {active_banks}: {specimens}')
specimens_to_skip = input("Enter the specimens to skip, separated by commas, or press enter to skip no specimens: ")
if specimens_to_skip:
    specimens_to_skip = [specimen.strip() for specimen in specimens_to_skip.split(',')]
    channels_to_skip = [channels[specimens.index(specimen)] for specimen in specimens_to_skip if specimen in specimens]
    print(f'specimens to skip: {specimens_to_skip}')
    specimens = [specimen for specimen in specimens if specimen not in specimens_to_skip]
    channels = [channel for channel in channels if channel not in channels_to_skip]

cycle_manager = CycleManager()
print('\nSpecimen cycle counts from cycle tracker json file:')
print('Specimen ID:\tlast cycle number\tlast cycle direction')

cqt_filenames = []
for specimen in specimens:
    #lookup cycle number for each specimen
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    cqt_filenames.append(f'{specimen}_CQT_after_{cycle}_cycles')
    print(f'{specimen}\t\t\t{cycle}\t\t\t{direction}')

#check that all the profiles for these specimens exist in the selected folder
suffixes = ['OCV_CHG', 'OCV_DCHG']
for specimen in specimens:
    for suffix in suffixes:
        profile_name = f'{specimen}_{suffix}.xml'
        profile_path = f'{profile_folder}/{profile_name}'
        if not os.path.isfile(profile_path):
            raise ValueError(f"Profile {profile_name} not found in {profile_folder}.")
print('\nAll profiles found for all specimens!\n')

input('Press enter to continue with test execution.')

test_runner = TestRunner(channels, test_title)
barcodes = test_runner.barcodes

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
test_runner.start_tests(channels, cqt_profile, cqt_savepath, cqt_filenames)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
for specimen in specimens:
   cycle_manager.update_cycle_tracker(specimen, 'CQT', increment=False)  #update cycle tracker
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

print('CQT successful! Bringing all cells to test temperature...')

test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60)

print('Starting OCV extraction, discharge direction.')
print('---------------------------------------------------------------')
print('Specimen ID:\tChannel ID\tCycle\tStart Result')

#start discharge direction OCV extractor
for specimen in specimens:
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    for bank in active_banks:
        if specimen in CONFIG.SPECIMENS_PER_BANK[bank]:
            channel = CONFIG.CHANNELS_PER_BANK[bank][CONFIG.SPECIMENS_PER_BANK[bank].index(specimen)]  #finds the channel for the specimen
    discharge_profile = f'{specimen}_OCV_DCHG.xml'
    discharge_profile_path = f'{profile_folder}/{discharge_profile}'       #builds the path to the discharge profile
    discharge_filename = f'{specimen}_OCV_DCHG_after_cycle_{cycle}'
    result = test_runner.start_tests([channel], discharge_profile_path, savepath, discharge_filename, verbose=False)   #starts the tests
    print(f'{specimen}\t\t{channel}\t\t{cycle}\t{result[0]}')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=5*24*60, verbose=False)
print('Discharge direction OCV test completed on all specimens.')
for specimen in specimens:
    cycle_manager.update_cycle_tracker(specimen, 'OCV_DCHG', increment=False)  #update cycle tracker


print('Starting OCV extraction, charge direction.')
print('---------------------------------------------------------------')
print('Specimen ID:\tChannel ID\tCycle\tStart Result')

#start charge direction OCV extractor
for specimen in specimens:
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    for bank in active_banks:
        if specimen in CONFIG.SPECIMENS_PER_BANK[bank]:
            channel = CONFIG.CHANNELS_PER_BANK[bank][CONFIG.SPECIMENS_PER_BANK[bank].index(specimen)]  #finds the channel for the specimen
    charge_profile = f'{specimen}_OCV_CHG.xml'
    charge_profile_path = f'{profile_folder}/{charge_profile}'       #builds the path to the discharge profile
    charge_filename = f'{specimen}_OCV_CHG_after_cycle_{cycle}'
    result = test_runner.start_tests([channel], charge_profile_path, savepath, charge_filename, verbose=False)   #starts the tests
    print(f'{specimen}\t\t{channel}\t\t{cycle}\t{result[0]}')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=5*24*60, verbose=False)
print('Charge direction OCV test completed on all specimens.')
for specimen in specimens:
    cycle_manager.update_cycle_tracker(specimen, 'OCV_CHG', increment=False)  #update cycle tracker


print('\nSpecimen status after tests.\n')
print('---------------------------------------------------------------')
summary_table = 'Specimen\tBarcode\t\tChannel\t\tLast Cycle\tLast Event\n'
for specimen in specimens:
    last_cycle, last_event = cycle_manager.get_last_cycle(specimen)       #checks to see the last cycle
    for bank in active_banks:
        if specimen in CONFIG.SPECIMENS_PER_BANK[bank]:
            chan = CONFIG.CHANNELS_PER_BANK[bank][CONFIG.SPECIMENS_PER_BANK[bank].index(specimen)]  #finds the channel for the specimen
    barcode = barcodes[specimens.index(specimen)]
    summary_table += f'{specimen}\t\t{barcode}\t{chan}\t\t{last_cycle}\t\t{last_event}\n'

print(summary_table)

#generate csv progress report and save copy of json tracker file
progress_reporter = ProgressReporter()
progress_reporter.generate_progress_report_csv()
progress_reporter.save_copy_cycle_tracker_json()

message = f'''OCV extraction tests completed in both directions for PT-5801. All data saved to {savepath}.
                       \n\nBank tested: {bank_request}
                       \n\nSpecimens tested: {specimens}
                       \n\nCells Tested: {barcodes}
                       \n\n{summary_table}'''

test_runner.send_email(f'{test_title} Complete', message)

print('Test complete. Exiting.')