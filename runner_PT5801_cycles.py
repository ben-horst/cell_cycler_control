import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager
import tkinter as tk
from tkinter import filedialog
import os

profile_parent_folder = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_tuned_profiles"
savepath = "G:/My Drive/Cell Test Data/PT5801/Cycles"
test_title = 'PT5801_Cycles'

cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 25

root = tk.Tk()
root.withdraw()  # Hide the root window

profile_folder = filedialog.askdirectory(initialdir=profile_parent_folder, title="Select Profile Folder")
if not profile_parent_folder:
    raise ValueError("No folder selected. Exiting.")

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
    print(f'specimens to skip: {specimens_to_skip}')
    specimens = [specimen for specimen in specimens if specimen not in specimens_to_skip]

cycles_to_complete = int(input('Enter the number of cycles to complete: '))
if cycles_to_complete <= 0:
    raise ValueError("Invalid number of cycles. Must be greater than 0.")

cycle_manager = CycleManager()
print('\nSpecimen cycle counts from cycle tracker json file:')
print('Specimen ID:\tlast cycle number\tlast cycle direction\tfilename')
print('---------------------------------------------------------------')

#for each specimen, lookup the cycle number and direction from the cycle tracker json file
filenames = []
for specimen in specimens:
    #lookup cycle number for each specimen
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    filenames.append(f'{specimen}_cycles_{cycle}-{cycle + cycles_to_complete}')
    print(f'{specimen}\t\t\t{cycle}\t\t\t{direction}')

#check that all the profiles for these specimens exist in the selected folder
suffixes = ['FC', 'SC', 'EX', 'ST']
for specimen in specimens:
    for suffix in suffixes:
        profile_name = f'{specimen}_{suffix}.xml'
        profile_path = f'{profile_folder}/{profile_name}'
        if not os.path.isfile(profile_path):
            raise ValueError(f"Profile {profile_name} not found in {profile_folder}.")
print('All profiles found for all specimens!')

print('Filenames to be created:')
for filename in filenames:
    print(filename)

input('Press enter to continue with test execution.')

test_runner = TestRunner(channels, test_title)
barcodes = test_runner.barcodes

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
test_runner.start_tests(channels, cqt_profile, cqt_savepath, filenames)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
for specimen in specimens:
   cycle_manager.update_cycle_tracker(specimen, 'CQT', increment=False)  #update cycle tracker

#set bank to charge temp and wait
#charge all cells
# set bank to discharge temp and wait
#discharge all cells
#repeat