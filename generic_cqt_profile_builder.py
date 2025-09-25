from core.xml_editor import ProfileEditor
import shutil
import os

base_file_folder = "G:/My Drive/Cell Test Profiles/Utilities"
base_file_name = "CQT_P45B_1C_4C.xml"
base_file_path = os.path.join(base_file_folder, base_file_name)
print(f'This will build an CQT profile based on {base_file_name}')

name = input('Enter cell name: ')
cap = float(input('Enter cell capacity, in Ah: '))
max_V = float(input('Enter cell max voltage: '))
min_V = float(input('Enter cell min voltage: '))

pulse_1C_rate = 1
pulse_4C_rate= 4

new_file_name = f'{name}_CQT.xml'
new_file_path = os.path.join(base_file_folder, new_file_name)

print(f'New QCT profile for {new_file_name} will be generated in {base_file_folder}')
resp = input('Press "y" to continue: ')
if resp != 'y':
    exit()

params_to_change = {
    'Step2_curr': ['Step2', 'Curr'],
    'Step2_CO_volt': ['Step2', 'Stop_Volt'],
    'Step3_curr': ['Step3', 'Curr'],
    'Step3_CO_volt': ['Step3', 'Stop_Volt'],
}
new_vals = {
    'Step2_curr': cap * pulse_1C_rate,
    'Step2_CO_volt': max_V,
    'Step3_curr': cap * pulse_4C_rate,
    'Step3_CO_volt': min_V,
    }

shutil.copy(base_file_path, new_file_path)   #copy the base file to the new directory
editor = ProfileEditor(new_file_path)
editor.update_test_profile_params(params_to_change, new_vals)

print('Profile generated!')