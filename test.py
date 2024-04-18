from test_manager import TestManager
import time

manager = TestManager()

#print(manager.get_bank_regulation_type('5802'))

print(manager.start_test_from_package(5801, 'test_packages/test_package.json'))