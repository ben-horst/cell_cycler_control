from core.xml_editor import ProfileEditor
import shutil
import os

base_file_folder = "G:/My Drive/Cell Test Profiles/RPTs"
base_file_name = "P45_RPT_V1.2.xml"
base_file_path = os.path.join(base_file_folder, base_file_name)
print(f'This will build an RPT profile based on {base_file_name}')

name = input('Enter cell name: ')
cap = input('Enter cell capacity, in Ah: ')
max_V = input('Enter cell max voltage: ')
min_V = input('Enter cell min voltage: ')

pulse_C_rate_low = 1
pulse_C_rate_high = 8

new_file_name = f'{name}_RPT'
new_file_path = os.path.join(base_file_folder, new_file_name)

print(f'New RPT for {new_file_name} will be generated in {base_file_folder}')
input('Press "y" to continue: ')

params_to_change = {
    'Step2_curr': ['Step2', 'Curr'],
    'Step2_CO_volt': ['Step2', 'Stop_Volt'],
    'Step4_curr': ['Step4', 'Curr'],
    'Step6_volt': ['Step6', 'Volt'],
    'Step6_curr': ['Step6', 'Curr'],
    'Step8_volt': ['Step8', 'Volt'],
    'Step8_curr': ['Step8', 'Curr'],
    'Step9_volt': ['Step9', 'Volt'],
    'Step9_curr': ['Step9', 'Curr'],
    'Step12_volt': ['Step12', 'Volt'],
    'Step12_curr': ['Step12', 'Curr'],
    'Step14_volt': ['Step14', 'Volt'],
    'Step14_curr': ['Step14', 'Curr'],
    'Step16_volt': ['Step16', 'Volt'],
    'Step16_curr': ['Step16', 'Curr'],
    'Step18_curr': ['Step18', 'Curr'],
    'Step18_cap': ['Step18', 'Cap'],
}
new_vals = {
    'Step2_curr': cap,
    'Step2_CO_volt': max_V,
    'Step4_curr': cap,
    'Step6_volt': max_V,
    'Step6_curr': cap,
    'Step8_volt': min_V,
    'Step8_curr': cap * pulse_C_rate_low,   #low pulse of pulse train
    'Step9_volt': min_V,
    'Step9_curr': cap * pulse_C_rate_high,  #high pulse of pulse train
    'Step12_volt': max_V,
    'Step12_curr': cap,
    'Step14_volt': min_V,
    'Step14_curr': cap,
    'Step16_volt': max_V,
    'Step16_curr': cap,
    'Step18_curr': cap,
    'Step18_cap': cap / 2
    }

shutil.copy(base_file_path, new_file_path)   #copy the base file to the new directory
editor = ProfileEditor(new_file_path)
editor.update_test_profile_params(params_to_change, new_vals)

print('Profile generated!')