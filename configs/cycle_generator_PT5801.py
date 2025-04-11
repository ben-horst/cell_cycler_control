#generates a json lookup table for the cycle type for every cycle in PT5801 for each specimen
#every cycle is either fast/slow charge and either extended/standard discharge

#also generates a blacnk cycle_tracker json to record most recent cycle count for each specimen

import json
from datetime import datetime
import PT5801 as CONFIG

def generate_cycle_lookup_table():
    loopkup_json_file = "./configs/PT5801_cycle_lookup.json"
    MAX_CYCLES = 10000  #max number of cycles to generate lookup table for

    input(f"Press enter to generate cycle lookup table for PT5801 through {MAX_CYCLES} cycles. This will overwrite the existing cycle lookup table at {loopkup_json_file}")
    conditions = CONFIG.SLOW_CHARGE_FREQUENCIES.keys()

    #lookup table structure: dictionary with conditions as keys, each accessing a disctionary with charge and discharge lists, whose index is the cycle number
    #values in lists are true when there is a slow charge or extended discharge, false otherwise
    cycle_lookup = dict.fromkeys(conditions, {})  #initialize the lookup table with empty lists for each cycle

    for condition in conditions:
        sc_freq = CONFIG.SLOW_CHARGE_FREQUENCIES[condition]
        ex_freq = CONFIG.EX_DISCHARGE_FREQUENCY

        #counters to increment every nominal event (fast charge or standard discharge)
        chg_counter = 0 
        dchg_counter = 0

        cycle_lookup[condition] = {'chg_slow': [None], 'dchg_ex': [None] }      #filling the zeroth spot with None as we will index from 1

        for i in range(1, MAX_CYCLES):
            chg_counter = round((chg_counter + sc_freq), 4)  #increment and round to 4 decimal places to avoid floating point errors
            if chg_counter >= 1: #once counter passes 1, add in a slow charge
                chg_counter = 0
                cycle_lookup[condition]['chg_slow'].append(True)
            else:
                cycle_lookup[condition]['chg_slow'].append(False)

            dchg_counter = round((dchg_counter + ex_freq), 4)  #increment and round to 4 decimal places to avoid floating point errors
            if dchg_counter >= 1:   #once counter passes 1, add in an extended discharge
                dchg_counter = 0
                cycle_lookup[condition]['dchg_ex'].append(True)
            else:
                cycle_lookup[condition]['dchg_ex'].append(False)

        #repeat for all conditions

    #save json file
    with open(loopkup_json_file, 'w') as f:
        json.dump(cycle_lookup, f, indent=4)

    print(f"Cycle lookup table generated and saved to {loopkup_json_file}.")

def generate_cycle_tracker():
    cycle_tracker_file = "./configs/PT5801_cycle_tracker.json"

    input(f"Press enter to generate blank cycle tracker json file. This will overwrite the existing cycle tracker file at {cycle_tracker_file}")
    all_specimens = []
    for sublist in CONFIG.SPECIMENS_PER_BANK.values():
        all_specimens.extend(sublist)
    
    #format of cycle tracker is a dictionary with specimen IDs as keys a dictionary containing the keys: "last_cycle_number", "last_cycle_direction", "last_cycle_datetime"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cycle_tracker = {}
    for specimen in all_specimens:
        cycle_tracker[specimen] = {'last_cycle_number': 0, 'last_cycle_direction': None, 'last_cycle_datetime': now}
    #save json file
    with open(cycle_tracker_file, 'w') as f:
        json.dump(cycle_tracker, f, indent=4)
    print(f"Cycle tracker file generated and saved to {cycle_tracker_file}.")


generate_cycle_lookup_table()
generate_cycle_tracker()