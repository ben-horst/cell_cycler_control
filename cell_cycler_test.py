from cell_cycler import CellCycler
import time

cycler = CellCycler()
#print(cycler.get_device_info())
#print(cycler.get_channels_status([270203,'270204']))
#print(cycler.stop_channels([270204])) 
#chan_data = cycler.get_channels_current_data([270203,270204])
#print(chan_data)
#print(chan_data[0].get('step_type'))
print(cycler.start_channels([270105], "C:/Users/cell.test/testpath"))