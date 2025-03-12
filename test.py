from core.xml_editor import profile_editor

filepath = "G:/.shortcut-targets-by-id/1-L4j121bGjSf--B6mGTPalBgTyvO_rtD/P2 Zip Battery World/Testing/Cell Test Data/Test Profiles/Cycle Tests/P45_cycle_test_V1.0.xml"

editor = profile_editor(filepath)

params_to_get = {
    'charge_voltage': ['Step2', 'Volt'],
    'charge_current': ['Step2', 'Curr'],
    'discharge_power': ['Step4', 'Pow'],
    'charge_cutoff': ['Step2', 'Stop_Curr'],
    'discharge capacity': ['Step8', 'Cap'],
    'cutoff_voltage': ['Step4', 'Stop_Volt'],
    'Time': ['Step15', 'Time']
}



params_to_edit = {
    'discharge capacity': ['Step8', 'Cap'],
    'cutoff_current': ['Step2', 'Stop_Curr'],
    'rest_time': ['Step1', 'Time']
}

new_params = {
    'discharge capacity': 0.4789999972222222,
    'cutoff_current': 1.03,
    'rest_time': 30
}

editor.update_test_profile_params(params_to_edit, new_params)

params = editor.get_current_params(params_to_get)
print(params)