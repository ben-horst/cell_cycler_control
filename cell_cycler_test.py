from cell_cycler import CellCycler
import time

cycler = CellCycler()
#print(cycler.get_device_info())
#print(cycler.get_channels_status([270203,'270204']))
#print(cycler.stop_channels([270105])) 
#chan_data = cycler.get_channels_current_data([270101])
#print(chan_data)
#print(chan_data[0].get('step_type'))
#print(cycler.continue_channels([270203])) 
#print(cycler.get_working_states([270203,270204]))
print(cycler.get_step_types([270101, 270102]))
profile = "C:/Users/cell.test/Documents/Unofficial Profiles/30s_rest.xml"
savepath = "C:/Users/cell.test/Documents/BackupData"
#print(cycler.start_channels([270105], profile, savepath, 'testname_cycle200'))
