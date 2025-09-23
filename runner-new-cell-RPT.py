
#run a multitemp water-cooled new cell RPT, RPT and cqt profiles selected by a user 
import os 
import sys 
import tkinter as tk
from tkinter import filedialog

from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager

# Force Tk window to stay hidden
root = tk.Tk()
root.withdraw()

# ask for creating test title and Results folder
test_title = input("Enter test title (e.g., PB45_PRT):")
if not test_title:
    print("Error: test title cannot be empty.")
    sys.exit(1)
test_title = test_title.strip().replace(" ", "_")
base_path = "G:/My Drive/Cell Test Data"
save_path = os.path.join(base_path, test_title)
cqt_savepath = save_path

# ask for a cqt-profile
cqt_profile_dir = r"G:/My Drive/Cell Test Profiles/cqt"
cqr_file_name = f"{test_title}_QCT"
if os.path.exists(cqt_profile_dir):
    init_dir = cqt_profile_dir
else:
    init_dir = None  # open default folder

cqt_profile = filedialog.askopenfilename(
    title="Select cqt_profile (.xml) file",
    initialdir=init_dir,
    filetypes=[("XML files", "*.xml")]
)
# Check if a profile was selected
if not cqt_profile:
    print("Error: No profile file selected. Exiting...")
    sys.exit(1)


# ask for RPT profile
RPT_dir = r"G:/My Drive/Cell Test Profiles/RPTs"
RPT_file_name = f"{test_title}_RPT"
if os.path.exists(RPT_dir):
    init_dir = RPT_dir
else:
    init_dir = None  # open default folder

RPT_profile = filedialog.askopenfilename(
    title="Select profile (.xml) file",
    initialdir=init_dir,
    filetypes=[("XML files", "*.xml")]
)
# Check if a profile was selected
if not RPT_profile:
    print("Error: No profile file selected. Exiting...")
    sys.exit(1)

# ask for channels 
valid_channels = {
    270101,270102,270103,270104,270105,270106,270107,270108,
    270201,270202,270203,270204,270205,270206,270207,270208,
    520101,520102,520103,520104,520105,520106,520107,520108,
    520201,520202,520203,520204,520205,520206,520207,520208,
    580101,580102,580103,580104,580105,580106,580107,580108,
    580201,580202,580203,580204,580205,580206,580207,580208,
    590101,590102,590103,590104,590105,590106,590107,590108,
    590201,590202,590203,590204,590205,590206,590207,590208,
}
channel_input = input("Enter channel numbers separated by commas (e.g., 270201,270205): ").strip()
if not channel_input:
    print("Error: No channels entered. Exiting...")
    sys.exit(1)
try:
    channels = [int(ch.strip()) for ch in channel_input.split(",") if ch.strip()]
except ValueError:
    print("Error: Invalid format. Channels must be numbers separated by commas.")
    sys.exit(1)
# Validate channels
for ch in channels:
    if ch not in valid_channels:
        print(f"Error: Channel {ch} is not valid.")
        sys.exit(1)

for ch in channels:
    print(f" - {ch} ({valid_channels[ch]})")

temps = [20, 35, 50]
cqt_temp = 25


test_runner = TestRunner(all_channels=channels, test_title=test_title, email_addresses='ben.horst@flyzipline.com,erneste.niyigena@flyzipline.com')

#perform connection quality check
print('Setting temperature for cell connection quality test...')
test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30)
test_runner.start_tests(channels, cqt_profile, cqt_savepath, cqr_file_name)
test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4)  
#the above only passes if all cells reach the "finish" state within the timeout, otherwise the program rasies exception and exits

for temp in temps:
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=30)
    test_runner.start_tests(channels=channels, profile=RPT_profile, savepath=save_path, filenames=RPT_file_name)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60*24)

test_runner.send_email(f'{test_title} Test Complete', f'All tests completed successfully.')