from cell_cycler import CellCycler
from chiller_controller import ChillerController
from barcode_manager import BarcodeManager
import time
import gmail

class TestRunner:
    def __init__(self, all_channels, test_title, ignored_banks=None, email_addresses='ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com'):
        self.all_channels = all_channels
        self.test_title = test_title
        self.ignored_banks = ignored_banks if ignored_banks else []
        self.banks = self.find_banks_used()
        self.bank_channels = self.update_bank_channels()
        self.chiller_controller = ChillerController(self.banks)
        self.barcode_manager = BarcodeManager()
        self.cycler = CellCycler()
        self.email = gmail.gmail()
        self.email_addresses = email_addresses
        self.barcodes = self.barcode_manager.barcodes_from_chlcodes(self.all_channels)
        input(f"This test runner will run {test_title} on {len(self.all_channels)} cells in banks {self.banks}.\nThe barcodes are {self.barcodes}.\nPress any enter to continue: ")

    def find_banks_used(self):
        banks = []
        for channel in self.all_channels:
            bank = channel // 100
            if bank not in banks:
                banks.append(bank)
        return banks

    def update_bank_channels(self):
        bank_channels = {}
        for bank in self.banks:
            channels_in_bank = []
            for i in range(1, 9):
                channels_in_bank.append(bank * 100 + i)
            bank_channels.update({bank: channels_in_bank})
        return bank_channels

    def bring_all_cells_to_temp_and_block_until_complete(self, temp, timeout_mins=60, temp_tolerance=5):
        print(f'setting chillers and starting blocking wait for all cells to reach within {temp_tolerance} deg of {temp} degC - timeout = {timeout_mins} minutes')
        start_time = time.time()
        temp_paddings = dict.fromkeys(self.banks, 0)
        chiller_targets = dict.fromkeys(self.banks, temp)
        temps_ok = dict.fromkeys(self.banks, False)
        for bank in self.banks:
            self.chiller_controller.set_temp(bank, chiller_targets[bank])
            print(f'chiller for {bank} set to {chiller_targets[bank]}degC')
        while True:
            if time.time() - start_time > timeout_mins * 60:
                self.send_email(f'{self.test_title} Test Aborted - Temperature Timeout', f'Cells failed to reach target temperature within {timeout_mins} minutes - aborting test. Bank temp_okay status: {temps_ok}')
                raise RuntimeError(f'failed to reach target temperature within {timeout_mins} minutes - aborting test')
            if all(temps_ok.values()):
                print(f'all cells reached within {temp_tolerance} deg of target temperature')
                break
            for bank in self.banks:
                if bank in self.ignored_banks:
                    print(f'Ignoring temperature checks for bank {bank}, but maintaining chiller settings.')
                    temps_ok[bank] = True
                    continue
                if not temps_ok[bank]:
                    chiller_temp = self.chiller_controller.read_temp(bank)
                    chan_data = self.cycler.get_channels_current_data(self.bank_channels[bank])
                    cell_temps = [float(chan.get('auxtemp')) for chan in chan_data]
                    if cell_temps:
                        min_cell_temp = min(cell_temps)
                        max_cell_temp = max(cell_temps)
                        print(f'bank {bank} -- chiller temp: {chiller_temp}  |  min cell temp: {min_cell_temp}  |  max cell temp: {max_cell_temp}')
                        if abs(temp - min_cell_temp) < temp_tolerance and abs(temp - max_cell_temp) < temp_tolerance:
                            print(f'bank {bank} cell target temp reached: {min_cell_temp}degC')
                            temps_ok[bank] = True
                        elif abs(chiller_targets[bank] - chiller_temp) < 1:
                            avg_cell_temp = (min_cell_temp + max_cell_temp) / 2
                            if avg_cell_temp < temp:
                                temp_paddings[bank] = temp_paddings[bank] + 1
                            elif avg_cell_temp > temp:
                                temp_paddings[bank] = temp_paddings[bank] - 1
                            chiller_targets[bank] = temp + temp_paddings[bank]
                            print(f'changing bank {bank} chiller setpoint to {chiller_targets[bank]}')
                            self.chiller_controller.set_temp(bank, chiller_targets[bank])
            time.sleep(30)
        print(f'Test completed. Ignored banks: {self.ignored_banks}')

    def start_tests(self, channels, profile, savepath, filenames):
        print(f'starting tests on channels {channels}')
        start_results = []
        if isinstance(filenames, str):
            start_data = self.cycler.start_channels(channels, profile, savepath, filenames)
            for item in start_data:
                start_results.append(item.get('start result'))
        else:
            if len(filenames) != len(channels):
                raise ValueError('Number of filenames must match number of channels')
            for filename, channel in zip(filenames, channels):
                start_data = self.cycler.start_channels([channel], profile, savepath, filename)
                for item in start_data:
                    start_results.append(item.get('start result'))
                time.sleep(0.5)
        print('all start requests sent - waiting for responses')
        time.sleep(10)
        print(f'start results: {start_results}')
        return start_results

    def wait_for_all_channels_to_finish_and_block_until_complete(self, timeout_mins=60*24*14):
        print(f'starting blocking wait for all channels to finish - timeout = {timeout_mins} minutes ({timeout_mins/(60*24)} days)')
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_mins * 60:
                self.send_email(f'{self.test_title} Test Aborted - Cell Completion Timeout', f'Channels failed to complete tests within timeout of {timeout_mins} minutes ({timeout_mins/(60*24)} days) - aborting test.')
                raise RuntimeError(f'failed to complete tests within timeout of {timeout_mins} minutes ({timeout_mins/(60*24)} days) - aborting test')
            chan_data = self.cycler.get_channels_current_data(self.all_channels)
            cell_states = [chan.get('workstatus') for chan in chan_data]
            if all(state == 'finish' for state in cell_states):
                print('all channels finished')
                break
            time.sleep(30)
