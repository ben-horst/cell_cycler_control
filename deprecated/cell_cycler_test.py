from cell_cycler import CellCycler
import time

cycler = CellCycler()
#print(cycler.get_device_info())
#print(cycler.get_channels_status([580201, 580202]))
#print(cycler.stop_channels([270105])) 
#chan_data = cycler.get_channels_current_data([580201, 580202])
#print(chan_data)
#print(chan_data[0].get('step_type'))
#print(cycler.continue_channels([270203])) 
#states = cycler.get_working_states([590101, 590102])
#print(states)
#states.get([270201, 270202])
#print(cycler.get_step_types([580201, 580202]))
channels = [590201]
# profile = "C:/Users/cell.test/Documents/Current Test Profiles/Single Charge-Discharge/test_profile.xml"
# savepath = "C:/Users/cell.test/Documents/BackupData"
# print(cycler.start_channels(channels, profile, savepath, 'likhi'))

print(cycler.get_channels_current_data(channels))