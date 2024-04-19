from cell_cycler import CellCycler
from fan_control import FanController
from chiller_controller import ChillerController
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
import time

class TestManager():
    """class to act as supervisory manager for all cell tests, starting and managing tests,
    controlling chillers & fans, communicating with dashboard"""
    def __init__(self, bank_config_path='bank_config.json', savepath="C:/Users/cell.test/Documents/BackupData"):
        self.chillers = ChillerController()
        self.fans = FanController()
        self.cycler = CellCycler()
        self.savepath = savepath
        self.bank_config_path = bank_config_path
        self.bank_config = {}
        self.update_bank_config()
        self.bank_status = {}
        self.initialize_bank_status()
        self.bank_update_interval = 10  #how often banks are polled for chiller, fan, cell statuses
        self.bank_update_thread = threading.Thread(target=self.update_bank_statuses_recurring, daemon=True)
        self.bank_control_interval = 10 #how often banks are controlled (fans on/off, chiller temps, repeats)
        self.bank_control_thread = threading.Thread(target=self.control_banks_recurring, daemon=True)

    def start_update_bank_statuses_recurring(self):
        self.bank_update_thread.start()
    
    def stop_update_bank_statuses_recurring(self):
        self.bank_update_thread.join()

    def update_bank_statuses_recurring(self):
        while True:
            self.update_bank_statuses()
            time.sleep(self.bank_update_interval)

    def start_bank_control_recurring(self):
        self.bank_control_thread.start()
    
    def stop_bank_control_recurring(self):
        self.bank_update_thread.join()

    def control_banks_recurring(self):
        while True:
            self.control_banks()
            time.sleep(self.bank_control_interval)

    def update_bank_statuses(self):
        """function to be called recurringly that checks all cells and updates bank status 'state' and 'active_cells' params
        also checks fan and chiller states and updates those params"""
        #iterate through all banks
        for bankid, status in self.bank_status.items():
            if self.get_bank_regulation_type(bankid) == 'water':
                temp = self.get_bank_chiller_temp(bankid)
                status.update({'chiller_temp': temp})
            if self.get_bank_regulation_type(bankid) == 'fan':
                state = self.get_bank_fanstate(bankid)
                status.update({'fan_state': state})
            #build list of all channel codes in this banks
            chlcodes_in_bank = self.cycler.build_chlcodes(bankid, [1,2,3,4,5,6,7,8])
            #poll for working states (working, pause, finish, stop)
            status.update({'cell_states': self.cycler.get_working_states(chlcodes_in_bank)})
            #poll for step (rest, cc, dc, cp, dp)
            status.update({'cell_steps': self.cycler.get_step_types(chlcodes_in_bank)})
            #look at all cells, and check for overall bank state. if there are any that aren't 'stopped' or 'finish', then bank is 'busy.
            channels_busy = []
            for chl_state in status.get('cell_states'):
                if chl_state == 'finish' or chl_state == 'stop':
                    channels_busy.append(False)
                else:
                    channels_busy.append(True)
                if any(channels_busy):
                    status.update({'state': 'busy'})
                else:
                    if status.get('repeats_remaining') > 0:
                        status.update({'state': 'ready_for_repeat'})
                    else:
                        status.update({'state': 'available'})

    def control_banks(self):
        """checks bank statuses - if state==ready_for_repeat, then chiller gets sent new temp and channels are run again"""

        #iterate through all banks
        for bankid, status in self.bank_status.items():
            if status.get('test_package') is None:  #exit if there isn't yet a test package loaded
                return
            #first check if a test has completed and is waiting for a repeat and temp change
            if status.get('state') == 'ready_for_repeat':
                start_result = self.send_test_start(bankid) #sets chiller to next temp and starts test
                #do we do something with start_result?
            elif status.get('state') == 'busy':
                self.command_fans_by_channel_step(bankid)
                self.continue_channels_if_all_paused(bankid)    #this is used to syncronize channels
            
    def command_fans_by_channel_step(self, bankid):
        """checks all of the channels that are active in a test
        if any are in a step that requires fan on (based on test profile) turns on"""

        package = self.bank_status.get(bankid).get('test_package')
        if package.get('regulation') == 'fan':
            all_channel_steps = self.bank_status.get(bankid.get('cell_steps'))
            channel_needs_fan = [] #true if channel is in step that needs fan
            for chl in package.get('channels'):
                step = all_channel_steps[chl-1]    #channels are 1 indexed
                needs_fan = any(step == item for item in package.get('fanonstates'))
                channel_needs_fan.append(needs_fan)
            #since there's only one fan per bank, if any of them are in a fan-on step, we turn on fans
            if any(channel_needs_fan):      
                self.set_bank_fan_on(bankid)
            else:
                self.set_bank_fan_off(bankid)
        else:
            return

    def continue_channels_if_all_paused(self, bankid):
        """if all active channels are paused, sends continue command"""
        package = self.bank_status.get(bankid).get('test_package')
        all_channel_states = self.bank_status.get(bankid).get('cell_states')
        channels_paused = [] #list, true if channel is paused
        for chl in package.get('channels'):
            state = all_channel_states[chl-1]    #channels are 1 indexed
            channels_paused.append(state == 'pause')
        if all(channels_paused):
            continue_result = self.continue_channels(bankid, package.get('channels'))


    def start_test_from_package(self, bankid, package_path, user_params={}):
        """takes in a json test package, modifies the test profile, start thermal regulation, then starts test
        also takes dictionary of parameters to be updated in the 'profile_params' field - keys must match those in the test package"""
        bankid = str(bankid)
        with open(package_path, 'r') as json_file:
            test_package = json.load(json_file)
        
        #check that bank is available
        if self.get_bank_state(bankid) != 'available':
            raise Exception('bank not available')
        
        #next check that the regulation type is appropriate - if regulation is requested it must match the type of the bank
        if test_package.get('regulation') is not None and test_package.get('regulation') != self.get_bank_regulation_type(bankid):
            raise Exception(f'{test_package.get('regulation')} regulation requested, bank has {self.get_bank_regulation_type(bankid)}')

        #modify the test profile, if needed
        num_params_to_update = len(test_package.get('profile_params'))
        params_updated = 0
        if num_params_to_update > 0:
            #must provide the right number of update params
            if len(user_params) != num_params_to_update:
                raise Exception(f'test package has {num_params_to_update} parameters to update, {len(user_params)} were given')
            #user param keys must match with package param keys
            if user_params.keys() != test_package.get('profile_params').keys():
                raise Exception(f'test package requires keys {test_package.get('profile_params').keys()}, keys given were {user_params.keys()}')
            #if any of the user params are None, that signals to NOT update profile
            if all(user_params.values()):
                params_updated = self.update_test_profile_params(test_package.get('profile'), test_package.get('profile_params'), user_params)

        #after all those checks, should be good to start test

        self.bank_status.get(bankid).update({'test_package': test_package})
        self.bank_status.get(bankid).update({'test_starttime': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")})
        self.bank_status.get(bankid).update({'repeats_remaining': test_package.get('repeats')})

        start_result = self.send_test_start(bankid)
        return start_result, params_updated
    
        
    def build_testheader(self, header_from_packet, bankid, regulation_type, temp=None):
        """builds the test header to be sent to the cycler to be in logfile name"""
        if regulation_type == 'fan':
            reg_string = '-fan_ctrl'
        elif regulation_type == 'water':
            reg_string = f'-water_ctrl-{int(temp)}C'
        else:
            reg_string = ''
        return header_from_packet + reg_string +'-bank_' + bankid + '-' + datetime.now().strftime("%m_%d_%Y")

    def send_test_start(self, bankid):
        """builds chlcode list, testheader, and sends start command to cycler - looks up needed info in bank_status --> test_package
        also starts chiller as needed"""
        #this has all the needed info
        package = self.bank_status.get(bankid).get('test_package')  

        #startup chiller, if needed, also turn off fan
        if package.get('regulation') == 'fan':
            self.set_bank_fan_off(bankid)
        start_temp = None
        if package.get('regulation') == 'water':
            start_temp = package.get('temps').pop(0)   #grab the 0th entry and remove it
            self.set_bank_chiller(bankid, start_temp)
        logfile_header = package.get('logfile_header')
        regulation = package.get('regulation')
        channels = package.get('channels')
        profile = package.get('profile')
        testheader = self.build_testheader(logfile_header, bankid, regulation, start_temp)

        #take the channels in form [1,2] and build chlcodes in form [580101, 580102]
        chlcodes = self.cycler.build_chlcodes(bankid, channels)
        #send start test command to cycler
        responses = self.cycler.start_channels(chlcodes, profile, self.savepath, testheader)
        self.bank_status.get(bankid).update({'state': 'busy'})
        #pull out the start result for each channel
        start_results = []
        for channel_response in responses:
            start_results.append(channel_response.get('start result'))
        return start_results
    
    
    def stop_channels(self, bankid, channels):
        chlcodes = self.cycler.build_chlcodes(bankid, channels)
        responses = self.cycler.stop_channels(chlcodes)
        stop_results = []
        for channel_response in responses:
            stop_results.append(channel_response.get('stop result'))
        return stop_results
    
    def continue_channels(self, bankid, channels):
        chlcodes = self.cycler.build_chlcodes(bankid, channels)
        responses = self.cycler.continue_channels(chlcodes)
        continue_results = []
        for channel_response in responses:
            continue_results.append(channel_response.get('continue result'))
        return continue_results
        
    def update_bank_config(self):
        with open(self.bank_config_path, 'r') as json_file:
            self.bank_config = json.load(json_file)

    def get_bank_regulation_type(self, bankid):
        return self.bank_config.get(bankid).get('regulation')
    
    def get_chiller_number(self, bankid):
        return self.bank_config.get(bankid).get('chiller')
    
    def get_fan_number(self, bankid):
        return self.bank_config.get(bankid).get('fanrelay')
    
    def get_bank_state(self, bankid):
        return self.bank_status.get(bankid).get('state')
    
    def initialize_bank_status(self):
        for key in self.bank_config:
            self.bank_status.update(
                {key: {
                    'state': 'available',
                    'test_package': None,
                    'test_starttime': None,
                    'repeats_remaining': 0,
                    'chiller_temp': None,
                    'fan_state': 'off',
                    'cell_states': [],
                    'cell_steps': []
                    }
                })

    def set_bank_chiller(self, bankid, temp):
        """"takes a bankid and temp setpoint, finds the matching chiller, then sends setpoint"""
        chiller_num = self.get_chiller_number(str(bankid))
        if chiller_num is None:
            raise Exception("no chiller on this bank")
        return self.chillers.set_temp(chiller_num, temp)

    def get_bank_chiller_temp(self, bankid):
        """"takes a bankid and temp setpoint, finds the matching chiller, then measures setpoint"""
        chiller_num = self.get_chiller_number(str(bankid))
        if chiller_num is None:
            raise Exception("no chiller on this bank")
        return self.chillers.read_temp(chiller_num)
    
    def set_bank_fan_on(self, bankid):
        """"takes a bankid, finds the fan relay, then turns it on"""
        fan_num = self.get_fan_number(str(bankid))
        if fan_num is None:
            raise Exception("no fan on this bank")
        return self.fans.turn_on(fan_num)
    
    def set_bank_fan_off(self, bankid):
        """"takes a bankid, finds the fan relay, then turns it on"""
        fan_num = self.get_fan_number(str(bankid))
        if fan_num is None:
            raise Exception("no fan on this bank")
        return self.fans.turn_off(fan_num)

    def get_bank_fanstate(self, bankid):
        fan_num = self.get_fan_number(bankid)
        return self.fans.get_relay_state(fan_num)
    

    def update_test_profile_params(self, profile_path, params_to_edit, new_params):
            """accepts a dictionary of parameters to edit, with each entry in the form
            "human readable param name": ["step#", "keyword"] and dicctionary of new values for those parameters
            with the same keys as params_to_edit along with path to xml file to edit"""
            prsr = ET.XMLParser(encoding="utf-8")
            tree = ET.parse(profile_path, parser=prsr)
            root = tree.getroot()
            for match in root.iter('Scale'):
                scale = int(match.get('Value'))
            params_updated = 0
            for key, val in params_to_edit.items():
                stepname = val[0]
                keywordname = val[1]
                for step in root.iter(stepname):       #go through all steps and look for matched string
                    for keyword in step.iter(keywordname):      #go through all the lines and looks for the keyword
                        val_from_user = new_params.get(key)
                        if val_from_user is None:
                            raise Exception("missing new parameter")
                        else:
                            if keyword.tag == 'Cap':    #since cap is stored in mAs, but user enters Ah
                                newval = str(int(float(val_from_user) * 3600 * 1000 * scale))
                            #can set other transforms for voltage, etc as needed
                            else:
                                newval = str(float(val_from_user) * scale)
                            keyword.set('Value', newval)
                            params_updated = params_updated + 1
            tree.write(profile_path)
            return params_updated

    