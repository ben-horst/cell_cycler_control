from test_manager import TestManager
import time

manager = TestManager()

manager.start_update_bank_statuses_recurring()
manager.start_bank_control_recurring()

time.sleep(3)
bank = '5901'

try:
    start_results, params_updated = manager.start_test_from_package(bank, 'test_packages/water_cool_test.json')
    print(f'start results: {start_results}')
except Exception as error:
    print('test start error: ', error)

while True:
    time.sleep(5)
    print(f'bank state: {manager.bank_status.get(bank).get('state')}')
    print(f'channel steps: {manager.bank_status.get(bank).get('cell_steps')}')
    print(f'chiller temp: {manager.get_bank_chiller_temp(bank)}')
