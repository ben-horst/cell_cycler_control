
import pandas as pd
import scipy.io
import shutil
import os
from datetime import datetime
from core.xml_editor import ProfileEditor
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
        vals = mat_contents.get('data')[:, :, -1]

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

mat_file = "C:/Users/local.user/Downloads/updated_sample_profile_update_file.mat"
base_file_path = "G:/.shortcut-targets-by-id/1-L4j121bGjSf--B6mGTPalBgTyvO_rtD/P2 Zip Battery World/Testing/Cell Test Data/PT-5801 - Empirical Cycle Testing/base_profiles"
output_file_path = "G:/.shortcut-targets-by-id/1-L4j121bGjSf--B6mGTPalBgTyvO_rtD/P2 Zip Battery World/Testing/Cell Test Data/PT-5801 - Empirical Cycle Testing/edited_profiles"

mat_extractor = MatExtractor(mat_file)


def build_new_charge_profiles(params_dict, base_file_path, output_file_path):
    # Create a new folder with today's date within output_file_path
    today_date = datetime.now().strftime("%Y-%m-%d")
    dated_output_path = os.path.join(output_file_path, today_date)
    os.makedirs(dated_output_path, exist_ok=True)

    for spec_id, params in params_dict.items():
        condition = spec_id[0:-2]  # get the condition from the specimen ID, chopping off the last two characters which represent replicate ID

        base_fc_profile = CONFIG.BASE_CHARGE_PROFILES[condition]['FC']
        fc_profile_path = f"{base_file_path}/{base_fc_profile}.xml"
        new_fc_profile_path = f"{dated_output_path}/{spec_id}_FC.xml"
        shutil.copy(fc_profile_path, new_fc_profile_path)   #copy the base file to the new directory
        ##open the new file and edit the parameters
        fc_editor = ProfileEditor(new_fc_profile_path)
        params_to_edit = {"charge_cutoff_current": [f"Step{CONFIG.CHARGE_TAPER_STEP}", "Stop_Curr"]}    #get the step number from the config file for where to edit the cutoff current
        updated_params = {"charge_cutoff_current": params['cutoff_current']}    #get the cutoff current value from the extracted data from the .mat
        fc_editor.update_test_profile_params(params_to_edit, updated_params)    #update the xml profile

        base_sc_profile = CONFIG.BASE_CHARGE_PROFILES[condition]['SC']
        sc_profile_path = f"{base_file_path}/{base_sc_profile}.xml"
        new_sc_profile_path = f"{dated_output_path}/{spec_id}_SC.xml"
        shutil.copy(sc_profile_path, new_sc_profile_path)  #copy the base file to the new directory


new_params = mat_extractor.build_params_dict()
build_new_charge_profiles(new_params, base_file_path, output_file_path)
#TODO: add the discharge profile building function here


