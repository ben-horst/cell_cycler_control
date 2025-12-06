# generates a json lookup table for the cycle type for every cycle in PT7526 for each specimen
# every cycle is either fast/slow charge and either extended/standard discharge
#
# also generates a blank cycle_tracker json to record most recent cycle count for each specimen

import json
from datetime import datetime
from configs import PT7526 as CONFIG


def _derive_conditions_from_specimens():
    # For PT-7526, frequencies are keyed by specimen IDs (e.g., E1R1, E1R2).
    # The cycle manager indexes the lookup by condition = specimen_id[:-2] (e.g., E1).
    all_specimens = []
    for sublist in CONFIG.SPECIMENS_PER_BANK.values():
        all_specimens.extend(sublist)
    conditions = {specimen[:-2] for specimen in all_specimens}
    return sorted(list(conditions))


def _get_sc_freq_for_condition(condition: str) -> float:
    # Find any specimen under this condition and use its slow charge frequency.
    # Assumes same frequency across replicates (e.g., E1R1 and E1R2 match).
    for specimen_id, freq in CONFIG.SLOW_CHARGE_FREQUENCIES.items():
        if specimen_id[:-2] == condition:
            return freq
    raise KeyError(f"No SLOW_CHARGE_FREQUENCIES entry found for condition '{condition}'")


def generate_cycle_lookup_table():
    loopkup_json_file = "./configs/PT7526_cycle_lookup.json"
    MAX_CYCLES = 10000  # max number of cycles to generate lookup table for

    input(
        f"Press enter to generate cycle lookup table for PT7526 through {MAX_CYCLES} cycles. "
        f"This will overwrite the existing cycle lookup table at {loopkup_json_file}"
    )

    conditions = _derive_conditions_from_specimens()

    # lookup table structure: dictionary with conditions as keys, each accessing a dictionary with
    # charge and discharge lists, whose index is the cycle number
    # values in lists are true when there is a slow charge or extended discharge, false otherwise
    cycle_lookup = {}

    for condition in conditions:
        sc_freq = _get_sc_freq_for_condition(condition)
        ex_freq = CONFIG.EX_DISCHARGE_FREQUENCY

        # counters to increment every nominal event (fast charge or standard discharge)
        chg_counter = 0
        dchg_counter = 0

        # filling the zeroth spot with None as we will index from 1
        cycle_lookup[condition] = {"chg_slow": [None], "dchg_ex": [None]}

        for i in range(1, MAX_CYCLES):
            chg_counter = round((chg_counter + sc_freq), 4)  # guard against floating point errors
            if chg_counter >= 1:  # once counter passes 1, add in a slow charge
                chg_counter = 0
                cycle_lookup[condition]["chg_slow"].append(True)
            else:
                cycle_lookup[condition]["chg_slow"].append(False)

            dchg_counter = round((dchg_counter + ex_freq), 4)  # guard against floating point errors
            if dchg_counter >= 1:  # once counter passes 1, add in an extended discharge
                dchg_counter = 0
                cycle_lookup[condition]["dchg_ex"].append(True)
            else:
                cycle_lookup[condition]["dchg_ex"].append(False)

        # repeat for all conditions

    # save json file
    with open(loopkup_json_file, "w") as f:
        json.dump(cycle_lookup, f, indent=4)

    print(f"Cycle lookup table generated and saved to {loopkup_json_file}.")


def generate_cycle_tracker():
    cycle_tracker_file = "./configs/PT7526_cycle_tracker.json"

    input(
        f"Press enter to generate blank cycle tracker json file. "
        f"This will overwrite the existing cycle tracker file at {cycle_tracker_file}"
    )
    all_specimens = []
    for sublist in CONFIG.SPECIMENS_PER_BANK.values():
        all_specimens.extend(sublist)

    # format of cycle tracker is a dictionary with specimen IDs as keys and a dictionary containing:
    # "last_cycle_number", "last_cycle_direction", "last_cycle_datetime"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cycle_tracker = {}
    for specimen in all_specimens:
        cycle_tracker[specimen] = {
            "last_cycle_number": 0,
            "last_cycle_direction": None,
            "last_cycle_datetime": now,
        }
    # save json file
    with open(cycle_tracker_file, "w") as f:
        json.dump(cycle_tracker, f, indent=4)
    print(f"Cycle tracker file generated and saved to {cycle_tracker_file}.")


print("blocking this to prevent accidental overwrite")
exit()
generate_cycle_lookup_table()
generate_cycle_tracker()


