import PT5801_config as CONFIG
from test_runner import TestRunner

profile = "C:/Users/cell.test/Documents/Current Test Profiles/RPTs/P45_RPT_V1.2.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-5801/RPTs"
temps = [20, 35, 50]
test_title = 'PT5801_RPTs'


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

filenames = []
for specimen in specimens:
    #TODO: add logic to lookup last completed cycle number for each specimen, for now hardcoding 0
    cycle = 0
    filenames.append(f'{specimen}_RPT_after_{cycle}_cycles')

test_runner = TestRunner(channels, test_title)

for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60)
    test_runner.start_tests(channels, profile, savepath, filenames)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*48)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.\n\nBanks used: {active_banks}\n\nSpecimens tested: {specimens}')