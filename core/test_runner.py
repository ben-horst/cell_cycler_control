# class to build test runners on top of

from core.cell_cycler import CellCycler
from core.chiller_controller import ChillerController
from core.barcode_manager import BarcodeManager
from core.gmail import Gmail
import time

class TestRunner:
    def __init__(self, all_channels, test_title, email_addresses='ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com'):
        self.all_channels = all_channels
        self.test_title = test_title
        self.banks = self.find_banks_used()
        self.bank_channels = self.update_bank_channels()
        self.chiller_controller = ChillerController(self.banks)
        self.barcode_manager = BarcodeManager()
        self.cycler = CellCycler()
        self.email = Gmail()
        self.email_addresses = email_addresses
        self.barcodes = self.barcode_manager.barcodes_from_chlcodes(self.all_channels)
        input(f"This test runner will run {test_title} on {len(self.all_channels)} cells in banks {self.banks}.\nThe barcodes are {self.barcodes}.\nPress enter to continue: ")

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
            for channel in self.all_channels:
                if channel // 100 == bank:  #add active channels into a dictionary per bank
                    channels_in_bank.append(channel)
            bank_channels.update({bank: channels_in_bank})
        return bank_channels
    
    def bring_all_cells_to_temp_and_block_until_complete(self, temp, timeout_mins=60, temp_tolerance=5, verbose=True):
        #commands all chillers to the target temperature, then waits for all cells to reach that temperature, bumping up/down chiller target if needed
        #this is blocking until the temperatures are achieved, but will abort if timeout (in minutes) is reached
        print(f'setting chillers and starting blocking wait for all cells to reach within {temp_tolerance} deg of {temp} degC - timeout = {timeout_mins} minutes')
        start_time = time.time()
        temp_paddings = dict.fromkeys(self.banks, 0)
        chiller_targets = dict.fromkeys(self.banks, temp)
        temps_ok = dict.fromkeys(self.banks, False)
        for bank in self.banks:
            try:
                self.chiller_controller.set_temp(bank, chiller_targets[bank])
                print(f'chiller for {bank} set to {chiller_targets[bank]}degC')
            except:
                self.send_email(f'{self.test_title} Test Aborted - Chiller Comms Failure.', f'Failed to set temperature on chiller for bank {bank} on port {self.chiller_controller.chillers.get(bank)}')
                raise RuntimeError(f'failed to set temperature on bank {bank} (port {self.chiller_controller.chillers.get(bank)})- aborting test')
        #wait for chillers to reach temp
        while True:
            if time.time() - start_time > timeout_mins * 60:
                self.send_email(f'{self.test_title} Test Aborted - Temperature Timeout', f'Cells failed to reach target temperature within {timeout_mins} minutes - aborting test. Bank temp_okay status: {temps_ok}')
                raise RuntimeError(f'failed to reach target temperature within {timeout_mins} minutes - aborting test')
            if all(temps_ok.values()):
                print(f'all cells reached within {temp_tolerance} deg of target temperature in {(time.time() - start_time) / 60:0.1f} mins')
                break
            for bank in self.banks:
                if not temps_ok[bank]:  #if the cells haven't yet reached the required temp
                    try:
                        chiller_temp = self.chiller_controller.read_temp(bank)
                    except:
                        self.send_email(f'{self.test_title} Test Aborted - Chiller Comms Failure.', f'Failed to read temperature on chiller for bank {bank} on port {self.chiller_controller.chillers.get(bank)}')
                        raise RuntimeError(f'failed to read temperature on bank {bank} (port {self.chiller_controller.chillers.get(bank)})- aborting test')
                    chan_data = self.cycler.get_channels_current_data(self.bank_channels[bank])
                    cell_temps = []
                    for chan in chan_data:
                        cell_temps.append(float(chan.get('auxtemp')))
                    min_cell_temp = min(cell_temps)
                    max_cell_temp = max(cell_temps)
                    print(f'bank {bank} -- chiller temp: {chiller_temp}  |  min cell temp: {min_cell_temp}  |  max cell temp: {max_cell_temp}') if verbose else None
                
                    if abs(temp - min_cell_temp) < temp_tolerance and abs(temp - max_cell_temp) < temp_tolerance:
                        print(f'bank {bank} cell target temp reached: {min_cell_temp}degC') if verbose else None
                        temps_ok[bank] = True
                    elif abs(chiller_targets[bank] - chiller_temp)  < 1:     #if the cell temp isn't reached, but the chiller temp has, then increase the chiller temp - needed due to heat loss to ambient
                        avg_cell_temp = (min_cell_temp + max_cell_temp) / 2
                        if avg_cell_temp < temp:
                            temp_paddings[bank] = temp_paddings[bank] + 1
                        elif avg_cell_temp > temp:
                            temp_paddings[bank] = temp_paddings[bank] - 1
                        chiller_targets[bank] = temp + temp_paddings[bank]
                        print(f'changing bank {bank} chiller setpoint to {chiller_targets[bank]}') if verbose else None
                    #keep resending the chiller target, in case the first transmission was lost
                    print(f'setting chiller to {chiller_targets[bank]}degC') if verbose else None
                    try:
                        self.chiller_controller.set_temp(bank, chiller_targets[bank])
                    except:
                        self.send_email(f'{self.test_title} Test Aborted - Chiller Comms Failure.', f'Failed to set temperature on chiller for bank {bank} on port {self.chiller_controller.chillers.get(bank)}')
                        raise RuntimeError(f'failed to set temperature on bank {bank} (port {self.chiller_controller.chillers.get(bank)})- aborting test')
            time.sleep(30)

    def start_tests(self, channels, profile, savepath, filenames, verbose=True):
        #starts tests on the given channels. May either provide a single filename for all tests, or a list of filenames for each channel
        print(f'starting tests on channels {channels}') if verbose else None
        start_results = []
        if type(filenames) == str:  #if a single filename is provided
            filename = filenames
            try:
                start_data = self.cycler.start_channels(channels, profile, savepath, filename)
            except:
                self.send_email(f'{self.test_title} Test Aborted - Cycler Comms Failure.', f'Failed to send start request to channels {channels}')
                raise RuntimeError(f'failed to send start request to channels {channels} - aborting test')
            for item in start_data:
                start_results.append(item.get('start result'))
        else:   #if individual filenames are provided
            if len(filenames) != len(channels):
                raise ValueError('Number of filenames must match number of channels')
            else:
                for filename, channel in zip(filenames, channels):
                    try:
                        start_data = self.cycler.start_channels([channel], profile, savepath, filename)
                    except:
                        self.send_email(f'{self.test_title} Test Aborted - Cycler Comms Failure.', f'Failed to send start request to channel {channel}')
                        raise RuntimeError(f'failed to send start request to channel {channel} - aborting test')
                    for item in start_data:
                        start_results.append(item.get('start result'))
                    time.sleep(0.5) #small delay between transmissions
        print('all start requests sent - waiting for responses') if verbose else None
        time.sleep(1)
        print(f'start results: {start_results})') if verbose else None
        if any(result != 'ok' for result in start_results):
            self.send_email(f'{self.test_title} Test Aborted - Cycler Start Failure', f'Some channels failed to start with responses: {start_results} on channels {channels} - aborting test.')
            raise RuntimeError(f'some channels failed to start with responses: {start_results} on channels {channels} - aborting test')
        return start_results

    def wait_for_all_channels_to_finish_and_block_until_complete(self, timeout_mins=60*24*14, verbose=True):
        #pings the cycler every 30 seconds to check if all channels have finished. Blocks until all channels are finished.
        #timeout is in minutes, defaulting to 2 weeks
        print(f'starting blocking wait for all channels to finish - timeout = {timeout_mins:.0f} minutes ({timeout_mins/(60*24):.2f} days)')
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout_mins * 60:
                self.send_email(f'{self.test_title} Test Aborted - Cell Completion Timeout', f'Channels failed to complete tests within timeout of {timeout_mins} minutes ({timeout_mins/(60*24)} days) - aborting test.')
                raise RuntimeError(f'failed to complete tests within timeout of {timeout_mins:.0f} minutes ({timeout_mins/(60*24):.2f} days) - aborting test')
            try:
                time.sleep(1) #small delay to prevent seeing channels "finished" before they started
                chan_data = self.cycler.get_channels_current_data(self.all_channels)
                cell_states = []
                cell_temps = []
                for chan in chan_data:
                    cell_states.append(chan.get('workstatus'))
                    cell_temps.append(float(chan.get('auxtemp')))
            except:
                self.send_email(f'{self.test_title} Test Aborted - Cycler Comms Failure.', f'Failed while requesting channel status on channels {self.all_channels}')
                raise RuntimeError(f'failed while requesting channel status on channels {self.all_channels} - aborting test')
            print(f'channel states: {cell_states}  |  channel temps: {cell_temps}') if verbose else None
            if all(state == 'finish' for state in cell_states):
                print(f'all channels finished in {(time.time() - start_time) / 60:0.1f} mins')
                break
            else:
                time.sleep(30)

    def send_email(self, subject, body):
        self.email.send_email(self.email_addresses, subject, body)
        print(f'email sent: {subject} to {self.email_addresses}')
    