from cell_cycler import CellCycler
import time

cycler = CellCycler()
#print(cycler.get_device_info()[3])
#print(cycler.get_channels_status([(27,2,3),(27,2,4)]))
#print(cycler.stop_channels([(27,2,3)])) 
chan_data = cycler.get_channels_current_data([(27,2,3),(27,2,4)])
#print(chan_data)
print(chan_data[0].get('step_type'))