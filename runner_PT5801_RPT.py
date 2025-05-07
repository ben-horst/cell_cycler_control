import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager

profile = "G:/My Drive/Cell Test Profiles/RPTs/P45_RPT_V1.2.xml"
savepath = "G:/My Drive/Cell Test Data/PT5801/RPTs"
temps = [20, 35, 50]
test_title = 'PT5801_RPTs'

cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 20

bank_request = input("Enter the banks for RPT execution, separated by commas, or enter 'ALL' to use all 6 banks: ")
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
    print(f'specimens to skip: {specimens_to_skip}')
    specimens = [specimen for specimen in specimens if specimen not in specimens_to_skip]

cycle_manager = CycleManager()
print('\nSpecimen cycle counts from cycle tracker json file:')
print('Specimen ID:\tlast cycle number\tlast cycle direction')

filenames = []
for specimen in specimens:
    #lookup cycle number for each specimen
    cycle, direction = cycle_manager.get_last_cycle(specimen)
    filenames.append(f'{specimen}_RPT_after_{cycle}_cycles')
    print(f'{specimen}\t\t\t{cycle}\t\t\t{direction}')

input('Press enter to continue with test execution.')

test_runner = TestRunner(channels, test_title)
barcodes = test_runner.barcodes

#perform connection quality check
#print('Setting temperature for cell connection quality test...')
#test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
#test_runner.start_tests(channels, cqt_profile, cqt_savepath, filenames)
#test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
#for specimen in specimens:
#    cycle_manager.update_cycle_tracker(specimen, 'CQT', increment=False)  #update cycle tracker
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

#start all the RPTs
for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60)
    filenames_with_temps = [f'{filename}_at_{temp}degC' for filename in filenames]
    test_runner.start_tests(channels, profile, savepath, filenames_with_temps)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*48)
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, 'RPT', increment=False)  #update cycle tracker

test_runner.send_email(f'{test_title} Test Complete',
                       f'''All tests completed successfully for multitemp RPT for PT-5801.
                       \n\nRPT temperatures: {temps} degC
                       \n\nBanks tested: {active_banks}
                       \n\nSpecimens tested: {specimens}
                       \n\nCells Tested: {barcodes}''')