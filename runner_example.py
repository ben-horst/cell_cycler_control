from core.test_runner import TestRunner

all_channels = [590107, 590108]
profile = "C:/Users/cell.test/Documents/Current Test Profiles/Specific Tests/rest_with_10Hz_log.xml"
savepath = "C:/Users/cell.test/Downloads/test"
cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 20

#filenames = 'sample_test'
filenames = ['sample1', 'sample2']
test_title = 'runner_test'
temps = [20,24]

test_runner = TestRunner(all_channels=all_channels, test_title=test_title, email_addresses='ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com')

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
test_runner.start_tests(all_channels, cqt_profile, cqt_savepath, filenames)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=30)
    test_runner.start_tests(channels=all_channels, profile=profile, savepath=savepath, filenames=filenames)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.')