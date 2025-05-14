import configs.PT5801 as CONFIG
from core.cycle_manager_PT5801 import CycleManager
import csv
import os
from datetime import datetime

class ProgressReporter():
    def __init__(self):
        self.savepath = "G:/My Drive/Cell Test Data/PT5801/Progress_Reports"
        self.cycle_manager = CycleManager()
        self.now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_progress_report_csv(self):

        all_specimens = []
        for specimens in CONFIG.SPECIMENS_PER_BANK.values():
            all_specimens.extend(specimens)

        all_channels = []
        for channels in CONFIG.CHANNELS_PER_BANK.values():
            all_channels.extend(channels)

        last_cycles = []
        last_directions = []
        last_datetimes = []
        for specimen in all_specimens:
            cycle, direction = self.cycle_manager.get_last_cycle(specimen)
            last_cycles.append(cycle)
            last_directions.append(direction)
            last_datetime = self.cycle_manager.get_last_cycle_datetime(specimen)
            last_datetimes.append(last_datetime)

        data = list(zip(all_specimens, all_channels, last_cycles, last_directions, last_datetimes))

        header = ['Specimen ID', 'Channel', 'Last Cycle Number', 'Last Cycle Direction', 'Last Cycle Datetime']
        os.makedirs(self.savepath, exist_ok=True)
        filename = os.path.join(self.savepath, f"progress_report_{self.now_str}.csv")
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
        print(f"Progress report saved to {filename}")

    def save_copy_cycle_tracker_json(self):
        # Save a copy of the cycle_tracker json to the same directory
        cycle_tracker_json_path = self.cycle_manager.cycle_tracker_file
        if os.path.isfile(cycle_tracker_json_path):
            json_copy_name = os.path.join(self.savepath, f"cycle_tracker_{self.now_str}.json")
            with open(cycle_tracker_json_path, 'r', encoding='utf-8') as src, open(json_copy_name, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            print(f"cycle_tracker json saved to {json_copy_name}")
        else:
            print("cycle_tracker json file not found.")
