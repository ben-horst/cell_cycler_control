#runs a multitemp water-cooled P30B and P45B cells, then charge/discharge to storage SOCs - see PT-5257

from core.test_runner import TestRunner
import configs.PT5257 as CONFIG

input("This script will run a multi-temp RPT for P30B and P45B cells, then charge to storage SOCs. Please ensure cells are loaded in bank 5802.\nPress enter to continue")
cycle_number = input("enter number of aging days accumulated: ")

test_title = 'PT5257_RPTs'

#P30B cells
profile_RPT_P30 = "G:/My Drive/Cell Test Profiles/RPTs/P30_RPT_V1.1.xml"
charge_profile_base_P30 = "G:/My Drive/Cell Test Profiles/Utilities/calendar_storage/P30B_charge_to"
savepath_P30 = "G:/My Drive/Cell Test Data/PT5257/P30B"
testname_base_P30 = f'P30B_PT5257_day_{cycle_number}'

#P45B cells
profile_RPT_P45 = "G:/My Drive/Cell Test Profiles/RPTs/P45_RPT_V1.1.xml"
charge_profile_base_P45 = "G:/My Drive/Cell Test Profiles/Utilities/calendar_storage/P45B_charge_to"
savepath_P45 = "G:/My Drive/Cell Test Data/PT5257/P45B"
testname_base_P45 = f'P45B_PT5257_day_{cycle_number}'

#CQT settings
prchg_profile = "G:/My Drive/Cell Test Profiles/Utilities/storage_charge_P45B.xml"
cqt_profile_P30 = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P30B_1C_4C.xml"
cqt_profile_P45 = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5257/CQTs"
cqt_temp = 25

all_channels = [580201, 580202, 580203, 580204, 580205, 580206, 580207, 580208]
updated_channels = []
temps = [20, 35, 50]

test_runner = TestRunner(all_channels, test_title)
barcodes = test_runner.barcodes
specimens = {}
for channel, barcode in zip(all_channels, barcodes):
    if barcode == "--EMPTY--":
        print(f"Removing channel {channel} because barcode is EMPTY")
        continue  # skip this one
    elif barcode.startswith('P30B'):
        is_P30B = True
    elif barcode.startswith('P45B'):
        is_P30B = False
    else:
        raise ValueError(f'Barcode {barcode} does not start with P30B or P45B')
    updated_channels.append(channel)
    storage_temp = CONFIG.SPECIMENS[barcode]['temp']
    storage_soc = CONFIG.SPECIMENS[barcode]['soc']
    specimens[channel] = {'barcode': barcode, 'storage_temp': storage_temp, 'storage_soc': storage_soc, 'is_P30B': is_P30B}


print('Current loaded cells in bank 5802:')
print('\n---------------------------------------------------------------')
print('Channel\t\tBarcode\t\tStorage temp\tStorage SOC')

for channel, data in specimens.items():
    barcode = data['barcode']
    storage_temp = data['storage_temp']
    storage_soc = data['storage_soc']
    is_P30B = data['is_P30B']
    print(f'{channel}\t\t{barcode}\t\t{storage_temp}\t\t{storage_soc}')

input('\nPress enter to start connection quality test (CQT)')

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30, verbose=False)
print('Charging cells before CQT.')
test_runner.start_tests(updated_channels, prchg_profile, cqt_savepath, 'PRCHG', verbose=False)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60, verbose=False) 
print('Starting CQTs.')
for channel, data in specimens.items():
    barcode = data['barcode']
    storage_temp = data['storage_temp']
    storage_soc = data['storage_soc']
    is_P30B = data['is_P30B']
    if is_P30B:
        cqt_name = f'{testname_base_P30}_CQT_stored_at_{storage_soc}soc_{storage_temp}degC'
        test_runner.start_tests([channel], cqt_profile_P30, cqt_savepath, cqt_name, verbose=False)
    else:
        cqt_name = f'{testname_base_P45}_CQT_stored_at_{storage_soc}soc_{storage_temp}degC'
        test_runner.start_tests([channel], cqt_profile_P45, cqt_savepath, cqt_name, verbose=False)

print('Waiting for CQTs to finish...')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4, verbose=False)  
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

print('\nCQT successful!\n')

for temp in temps:
    print(f'Bringing cells to {temp} degC for RPT')
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60, verbose=False)
    print('---------------------------------------------------------------')
    print('Channel\t\tBarcode\t\tStart Result')
    for channel, data in specimens.items():
        barcode = data['barcode']
        storage_temp = data['storage_temp']
        storage_soc = data['storage_soc']
        is_P30B = data['is_P30B']
        if is_P30B:
            rpt_name = f'{testname_base_P30}_RPT_at_{temp}_stored_at_{storage_soc}soc_{storage_temp}degC'
            result = test_runner.start_tests([channel], profile_RPT_P30, savepath_P30, rpt_name, verbose=False)
        else:
            rpt_name = f'{testname_base_P45}_RPT_at_{temp}_stored_at_{storage_soc}soc_{storage_temp}degC'
            result = test_runner.start_tests([channel], profile_RPT_P45, savepath_P45, rpt_name, verbose=False)
        print(f'{channel}\t\t{barcode}\t\t{result[0]}')
    print(f'Waiting for {temp} degC RPTs to finish...')
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*24*2, verbose=False)
       

print('\nall RPTs completed - setting chiller to 25 C and charging cells to storage SOCs\n')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=25, timeout_mins=60, verbose=False)
print('---------------------------------------------------------------')
print('Channel\t\tBarcode\t\tStorage SOC\tStart Result')

for channel, data in specimens.items():
    barcode = data['barcode']
    storage_temp = data['storage_temp']
    storage_soc = data['storage_soc']
    is_P30B = data['is_P30B']
    if is_P30B:
        charge_testname = f'{testname_base_P30}_charge_to_{storage_soc}soc'
        charge_profile = f"{charge_profile_base_P30}_{storage_soc}SOC.xml"
        result = test_runner.start_tests([channel], charge_profile, savepath_P30, charge_testname, verbose=False)
    else:
        charge_testname = f'{testname_base_P45}_charge_to_{storage_soc}soc'
        charge_profile = f"{charge_profile_base_P45}_{storage_soc}SOC.xml"
        result = test_runner.start_tests([channel], charge_profile, savepath_P45, charge_testname, verbose=False)
    print(f'{channel}\t\t{barcode}\t\t{storage_soc}\t\t{result[0]}')
print('\nWaiting for storage charges to finish...')
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*4, verbose=False)
        
print('All storage charges completed. Test completed.')

summary_table = 'Channel\t\tBarcode\t\tStorage temp\tStorage SOC'
for channel, data in specimens.items():
    barcode = data['barcode']
    storage_temp = data['storage_temp']
    storage_soc = data['storage_soc']
    is_P30B = data['is_P30B']
    summary_table += f'\n{channel}\t\t{barcode}\t\t{storage_temp}\t\t{storage_soc}'

message = f'PT-5257 calendar aging multi-temp RPT completed for the following cells: \n{summary_table}\n Please return cells to aging chamber and start next test.'
test_runner.send_email(f'{test_title} Complete', message)

print('Test complete. Exiting.')