from test_manager import TestManager
import time

manager = TestManager()

update_params = {
    "cutoffAh": None
    }
# try:
#     params_updated, start_results = manager.start_test_from_package(5901, 'test_packages/test_package.json', update_params)
#     #print(params_updated)
#     print(start_results)
# except Exception as error:
#     print('test start error: ', error)


print(manager.stop_channels(5901, [1,2]))

#manager.update_bank_statuses()
#exitprint(manager.bank_status.get('5901'))
#manager.start_update_bank_statuses_recurring()

while True:
    time.sleep(5)
    print(manager.bank_status.get('5901').get('state'))
