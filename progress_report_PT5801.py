import configs.PT5801 as CONFIG
from core.cycle_manager_PT5801 import CycleManager

cycle_manager = CycleManager()

input('This script generates a progress report and saves a copy of the cycle_tracker json. Press enter to continue.')

all_specimens = 

summary_table = 'Specimen\tBarcode\t\tChannel\t\tLast Cycle\tLast Event\n'
for specimen in specimens:
    last_cycle, last_event = cycle_manager.get_last_cycle(specimen)       #checks to see the last cycle
    chan = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]  #finds the channel for the specimen
    barcode = barcodes[specimens.index(specimen)]
    summary_table += f'{specimen}\t\t{barcode}\t{chan}\t\t{last_cycle}\t\t{last_event}\n'