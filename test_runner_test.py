from test_runner import TestRunner

channels = [590107, 590108]
profile = "C:/Users/cell.test/Documents/Current Test Profiles/????"
savepath = "C:/Users/cell.test/Documents/Test Data/????"
filenames = ['sample1', 'sample2']
test_title = 'runner_test'
temps = [25,35]

test_runner = TestRunner(allchanels=channels, test_title=test_title, email_addresses='ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com')

for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=60)
    test_runner.start_tests(channels=channels, profile=profile, savepath=savepath, filenames=filenames)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.')