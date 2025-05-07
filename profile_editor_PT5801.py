
import pandas as pd
import scipy.io
import shutil
import os
from datetime import datetime
from core.xml_editor import ProfileEditor
import tkinter as tk
from tkinter import filedialog
import configs.PT5801 as CONFIG

class MatExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.build_data()

    def build_data(self):
        #loads a .mat file at the specified path and returns a pandas dataframe with the data in usable form

        # Load the .mat file
        mat_contents = scipy.io.loadmat(self.file_path)
        #grab the last slice of the 3D array (most recent values)
        if len(mat_contents.get('data').shape) == 3:
            vals = mat_contents.get('data')[:, :, -1]
        elif len(mat_contents.get('data').shape) == 2:
            vals = mat_contents.get('data')[:, :]
        else:
            raise ValueError('.mat file not correct dimensions')

        #grab the column names from char array and convert to list - the value 0 is replaced with 'capacity'
        column_names = mat_contents.get('column_names').flatten()
        column_names = ['capacity' if name == 0 else name for name in column_names]

        #grab the specimen ids and barcodes
        specimen_ids = mat_contents.get('test_conditions').flatten()
        specimen_ids = [specimen_id.replace('xx', '') for specimen_id in specimen_ids]  #get rid of leading 'xx' on some specimen ids
        barcodes = mat_contents.get('barcodes').flatten()

        #build dataframe and add specimen_id and barcodes
        data = pd.DataFrame(vals, columns=column_names)
        data.insert(0, 'specimen_id', specimen_ids)
        data.insert(1, 'barcode', barcodes)

        return data

    def get_cutoff_current(self, spec_id, temp):
        #returns the cutoff current for the specified specimen and temperature
        if temp not in self.data.columns:
            raise ValueError(f'Temperature {temp} not found in data columns')
        row = self.data[(self.data['specimen_id'] == spec_id)]
        if row.empty:
            raise ValueError(f'Specimen ID {spec_id} not found in data')
        val = row[temp].values[0]
        return val
    
    def get_capacity(self, spec_id):
        #returns the capacity for the specified specimen
        row = self.data[(self.data['specimen_id'] == spec_id)]
        if row.empty:
            raise ValueError(f'Specimen ID {spec_id} not found in data')
        val = row['capacity'].values[0]
        return val
    
    def build_params_dict(self):
    # creates a dictionary of new parameters for each specimen, pulling from .mat file
        new_params = {}
        for bank in CONFIG.AVAILABLE_BANKS:
            for spec_id in CONFIG.SPECIMENS_PER_BANK[bank]:
                charge_temp = CONFIG.BANK_CHARGE_TEMPS[bank]
                cutoff_current = self.get_cutoff_current(spec_id, charge_temp)
                cell_capacity = self.get_capacity(spec_id)
                new_params[spec_id] = {'cutoff_current': cutoff_current, 'cell_capacity': cell_capacity}
        return new_params

def build_new_profiles(params_dict, base_file_path, output_file_path):
    # Create a new folder with today's date within output_file_path
    today_date = datetime.now().strftime("%Y-%m-%d")
    dated_output_path = os.path.join(output_file_path, today_date)
    os.makedirs(dated_output_path, exist_ok=True)

    print(f"Creating new profiles in {dated_output_path}")
    print("Spec ID\t\tCutoff Curr\tCell Capacity\tEX dchg time\tST dchg time")

    for spec_id, params in params_dict.items():
        condition = spec_id[0:-2]  # get the condition from the specimen ID, chopping off the last two characters which represent replicate ID

        #fast charge
        base_fc_profile = CONFIG.BASE_CHARGE_PROFILES[condition]['FC']
        fc_profile_path = f"{base_file_path}/{base_fc_profile}.xml"
        new_fc_profile_path = f"{dated_output_path}/{spec_id}_FC.xml"
        fc_params = {"charge_cutoff_current": [f"Step{CONFIG.CHARGE_TAPER_STEP}", "Stop_Curr"]}    #get the step number from the config file for where to edit the cutoff current
        fc_param_vals = {"charge_cutoff_current": params['cutoff_current']}    #get the cutoff current value from the extracted data from the .mat
        shutil.copy(fc_profile_path, new_fc_profile_path)   #copy the base file to the new directory
        fc_editor = ProfileEditor(new_fc_profile_path) #open the new file and edit the parameters
        fc_editor.update_test_profile_params(fc_params, fc_param_vals)    #update the xml profile

        #slow charge
        base_sc_profile = CONFIG.BASE_CHARGE_PROFILES[condition]['SC']
        sc_profile_path = f"{base_file_path}/{base_sc_profile}.xml"
        new_sc_profile_path = f"{dated_output_path}/{spec_id}_SC.xml"
        shutil.copy(sc_profile_path, new_sc_profile_path)  #copy the base file to the new directory

        #discharges
        dchg_times = {'EX': 0, 'ST': 0}
        for type in ['EX', 'ST']:
            base_dc_profile = CONFIG.DISCHARGE_PROFILES[type]
            dc_profile_path = f"{base_file_path}/{base_dc_profile}"
            new_dc_profile_path = f"{dated_output_path}/{spec_id}_{type}.xml"
            total_wh = params['cell_capacity'] * CONFIG.P45B_NOM_V
            wh_to_discharge = CONFIG.DISCHARGE_DEPTHS[condition][type] * total_wh   #depth of discharge * measured total capacity of cell
            wh_in_varied_step = wh_to_discharge - CONFIG.DISCHARGE_FIXED_WH[type]
            s_in_varied_step = 3600 * wh_in_varied_step / CONFIG.DISCHARGE_POWER_VARIED_STEP[type]
            dc_params = {"discharge_time": [f"Step{CONFIG.DISCHARGE_VARIED_STEP}", "Time"]}    #get the step number from the config file for where to edit the varied discharge time
            dc_param_vals = {"discharge_time": s_in_varied_step}
            dchg_times[type] = s_in_varied_step
            shutil.copy(dc_profile_path, new_dc_profile_path)   #copy the base file to the new directory
            dc_editor = ProfileEditor(new_dc_profile_path)  #open the new file and edit the parameters
            dc_editor.update_test_profile_params(dc_params, dc_param_vals)  
            
        print(f"{spec_id}\t\t{params['cutoff_current']:.2f} A\t\t{params['cell_capacity']:.2f} Ah\t\t{int(dchg_times['EX'])} s\t\t{int(dchg_times['ST'])} s")

root = tk.Tk()
root.withdraw()  # Hide the root window
mat_file = filedialog.askopenfilename(
    title="Select a .mat file",
    filetypes=[("MAT files", "*.mat")]
)
if not mat_file:
    raise ValueError("No .mat file selected")

base_file_path = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_base_profiles"
output_file_path = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_tuned_profiles"

mat_extractor = MatExtractor(mat_file)

new_params = mat_extractor.build_params_dict()
build_new_profiles(new_params, base_file_path, output_file_path)
