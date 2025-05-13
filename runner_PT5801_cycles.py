import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager
import tkinter as tk
from tkinter import filedialog

profile_parent_folder = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_tuned_profiles"
savepath = "G:/My Drive/Cell Test Data/PT5801/Cycles"
test_title = 'PT5801_Cycles'

cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
cqt_temp = 20

input('Please ensure that the profile_editor_PT5801 has been run.')

root = tk.Tk()
root.withdraw()  # Hide the root window

profile_folder = filedialog.askdirectory(initialdir=profile_parent_folder, title="Select Profile Folder")
if not profile_parent_folder:
    raise ValueError("No folder selected. Exiting.")

cycle_manager = CycleManager()

