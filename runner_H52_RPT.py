from core.test_runner import TestRunner

all_channels = [590101, 590102]
profile = "G:/My Drive/Cell Test Profiles/RPTs/H52_RPT_V1.2.xml"
savepath = "G:/My Drive/Cell Test Data/PT6598"
cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 20

filenames = 'PT6598-LG-H52-RPT'
test_title = 'runner_test'
temps = [35,50]

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
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*24)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.')