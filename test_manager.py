from cell_cycler import CellCycler
from fan_control import FanController
from chiller_controller import ChillerController
import json
import xml.etree.ElementTree as ET
from datetime import datetime

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
        

    def start_test_from_package(self, bankid, package_path, *user_params):
        """takes in a json test package, modifies the test profile, start thermal regulation, then starts test
        also takes list of parameters to be updated in the 'profile_params' field"""
        bankid = str(bankid)
        with open(package_path, 'r') as json_file:
            test_package = json.load(json_file)
        #check that bank is available
        if self.get_bank_state(bankid) != 'stopped':
            return 'bank busy'
        #next check that the regulation type is appropriate - if regulation is requested it must match the type of the bank
        if test_package.get('regulation') is not None and test_package.get('regulation') != self.get_bank_regulation_type(bankid):
            return f'{test_package.get('regulation')} regulation requested, bank has {self.get_bank_regulation_type(bankid)}'
        #modify the test profile, if needed
        num_params_to_update = len(test_package.get('profile_params'))
        if num_params_to_update > 0:
            if len(user_params) != num_params_to_update:
                return f'test package has {num_params_to_update} parameters to update, {len(user_params)} were given'
            #self.update_test_profile_params(profile_path, params_to_edit, new_params)
            #THIS IS WHERE I LEFT OFF
        chlcodes = self.cycler.build_chlcodes(bankid, test_package.get('channels'))
        testheader = test_package.get('logfile_header') + '-bank_' + bankid + '-' + datetime.now().strftime("%m_%d_%Y")
        return 'now start test!'
        
        
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
                    'state': 'stopped',
                    'test': None, 
                    'description': None,
                    'test_started': None,
                    'repeats_remaining': 0,
                    'chiller_temp': -55,
                    'fan_state': 'off',
                    'cells_active': 0
                    }
                })

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