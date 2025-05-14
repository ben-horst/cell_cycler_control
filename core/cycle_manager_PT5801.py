import json
from datetime import datetime

#this class manages the cycle lookup table for PT5801 and updates the cycle tracker json file
# this is used by the RPT and cycler runner scripts to track the last cycle completed and start the approriate charge and discharge events for each specimen

class CycleManager:
    def __init__(self):
        self.cycle_lookup_file = "./configs/PT5801_cycle_lookup.json"
        self.cycle_tracker_file = "./configs/PT5801_cycle_tracker.json"

    def get_charge_type(self, cycle_number, specimen_id):
        #returns the charge type for the specified cycle number and specid
        condition = specimen_id[:-2]
        with open(self.cycle_lookup_file, 'r') as f:
            cycle_lookup = json.load(f)
        is_slow_charge = cycle_lookup[condition]['chg_slow'][cycle_number]
        
        return 'sc' if is_slow_charge else 'fc'

    def get_discharge_type(self, cycle_number, specimen_id):
        #returns the discharge type for the specified cycle number and specid
        condition = specimen_id[:-2]
        with open(self.cycle_lookup_file, 'r') as f:
            cycle_lookup = json.load(f)
        is_extended_discharge = cycle_lookup[condition]['dchg_ex'][cycle_number]
        
        return 'ex' if is_extended_discharge else 'st'
    
    def get_last_cycle(self, specimen_id):
        #returns the last cycle number for the specified specimen from the cycle tracker json file
        with open(self.cycle_tracker_file, 'r') as f:
            cycle_tracker = json.load(f)

        if specimen_id not in cycle_tracker:
            raise Exception(f"Specimen ID {specimen_id} not found in cycle tracker. Please check the specimen ID and try again.")

        last_cycle_number = cycle_tracker[specimen_id]['last_cycle_number']
        last_cycle_direction = cycle_tracker[specimen_id]['last_cycle_direction']
        
        return last_cycle_number, last_cycle_direction
    
    def get_last_cycle_datetime(self, specimen_id):
        #returns the last cycle datetime for the specified specimen from the cycle tracker json file
        with open(self.cycle_tracker_file, 'r') as f:
            cycle_tracker = json.load(f)

        if specimen_id not in cycle_tracker:
            raise Exception(f"Specimen ID {specimen_id} not found in cycle tracker. Please check the specimen ID and try again.")

        last_cycle_datetime = cycle_tracker[specimen_id]['last_cycle_datetime']
        
        return last_cycle_datetime

    def update_cycle_tracker(self, specimen_id, direction, increment=False):
        #updates the cycle tracker json file with the last cycle completed for the specified specimen and direction (charge/discharge)
        if direction not in ['CHG', 'DCHG', 'RPT', 'CQT', 'STRG']:
            raise ValueError(f"Invalid direction '{direction}'. Must be 'CHG', 'DCHG', 'RPT', 'CQT', 'STRG'.")
        
        with open(self.cycle_tracker_file, 'r') as f:
            cycle_tracker = json.load(f)

        if specimen_id not in cycle_tracker:
            raise Exception(f"Specimen ID {specimen_id} not found in cycle tracker. Please check the specimen ID and try again.")

        cycle_tracker[specimen_id]['last_cycle_number'] += 1 if increment else 0
        cycle_tracker[specimen_id]['last_cycle_direction'] = direction
        cycle_tracker[specimen_id]['last_cycle_datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.cycle_tracker_file, 'w') as f:
            json.dump(cycle_tracker, f, indent=4)