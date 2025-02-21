from test_runner import TestRunner

all_channels = [590107, 590108]
profile_charge_P45B00071 = "C:/Users/cell.test/Documents/Current Test Profiles/P45_improved_OCV/P45B00071_OCV_V1.0_chg.xml"
profile_charge_P45B00072 = "C:/Users/cell.test/Documents/Current Test Profiles/P45_improved_OCV/P45B00072_OCV_V1.0_chg.xml"
profile_discharge_P45B00071 = "C:/Users/cell.test/Documents/Current Test Profiles/P45_improved_OCV/P45B00071_OCV_V1.0_dchg.xml"
profile_discharge_P45B00072 = "C:/Users/cell.test/Documents/Current Test Profiles/P45_improved_OCV/P45B00072_OCV_V1.0_dchg.xml"
savepath = "C:/Users/cell.test/Documents/Test Data/PT-6436"
test_title = 'PT6436_OCV_test'
charge_filenames = test_title + '_charge'
discharge_filenames = test_title + '_discharge'
temps = [35]

test_runner = TestRunner(all_channels, test_title)

for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp)
    test_runner.start_tests(channels=[590107], profile=profile_discharge_P45B00071, savepath=savepath, filenames=discharge_filenames)
    test_runner.start_tests(channels=[590108], profile=profile_discharge_P45B00072, savepath=savepath, filenames=discharge_filenames)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete()
    test_runner.start_tests(channels=[590107], profile=profile_charge_P45B00071, savepath=savepath, filenames=charge_filenames)
    test_runner.start_tests(channels=[590108], profile=profile_charge_P45B00072, savepath=savepath, filenames=charge_filenames)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.')