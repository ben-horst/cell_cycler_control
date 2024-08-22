from test_manager import TestManager
import time
from thingsboard import Thingsboard

manager = TestManager()
thingsboard = Thingsboard()

update_params = {
    "cutoffAh": None
    }
try:
    params_updated, start_results = manager.start_test_from_package(5901, 'test_packages/test_package.json', update_params)
    #print(start_results)
except Exception as error:
    print('test start error: ', error)

manager.start_status_and_control_checkers()

while True:
    time.sleep(5)
    #print(manager.bank_status)
    thingsboard.sendTelemetry(manager.get_all_banks_statuses())