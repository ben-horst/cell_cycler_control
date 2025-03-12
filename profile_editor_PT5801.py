
import pandas as pd
import scipy.io
from core.xml_editor import profile_editor
import configs.PT5801 as CONFIG

class mat_extractor:
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

mat_file = "C:/Users/local.user/Downloads/profile_update_file (2).mat"
mat_extractor = mat_extractor(mat_file)

all_specimens = [spec for specs_per_bank in CONFIG.SPECIMENS_PER_BANK.values() for spec in specs_per_bank]

for spec_id in all_specimens:
    cutoff_current_20 = mat_extractor.get_cutoff_current(spec_id, 20)
    cutoff_current_30 = mat_extractor.get_cutoff_current(spec_id, 30)
    cutoff_current_40 = mat_extractor.get_cutoff_current(spec_id, 40)
    cutoff_current_55 = mat_extractor.get_cutoff_current(spec_id, 55)
    capacity = mat_extractor.get_capacity(spec_id)
    print(f'Specimen ID: {spec_id}, 20C: {cutoff_current_20}, 30C: {cutoff_current_30}, 40C: {cutoff_current_40}, 55C: {cutoff_current_55}, Capacity: {capacity}')