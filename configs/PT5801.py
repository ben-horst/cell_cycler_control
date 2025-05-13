AVAILABLE_BANKS = [2701, 2702, 5201, 5202, 5801, 5901]

BANK_CHARGE_TEMPS = {
    2701: 30,
    2702: 40,
    5201: 30,
    5202: 40,
    5801: 55,
    5901: 40
}

DISCHARGE_TEMP = 40

CHANNELS_PER_BANK = {   #active channel numbers for each bank
    2701: [270101, 270102, 270103, 270104],
    2702: [270201, 270202, 270205, 270206, 270207, 270208],
    5201: [520101, 520102, 520103, 520104, 520105, 520107],
    5202: [520201, 520202, 520203, 520204, 520205, 520206],
    5801: [580101, 580102, 580103, 580104],
    5901: [590101, 590102, 590103, 590104, 590105, 590106, 590107, 590108]
}

SPECIMENS_PER_BANK = {  #specimen IDs for each bank
    2701: ['T1C1R1', 'T1C1R2', 'T2C1R1', 'T2C1R2'],
    2702: ['T9C1R1', 'T9C1R2',  'C0R1',   'C0R2',   'T3C1R1', 'T3C1R2'],
    5201: ['T7C1R1', 'T7C1R2', 'T7C2R1', 'T7C2R2', 'T7C3R1', 'T8C1R1'],
    5202: ['T2C3R1', 'T2C3R2', 'T4C1R1', 'T4C1R2', 'T4C2R1', 'T4C2R2'],
    5801: ['T1C2R1', 'T1C2R2', 'T2C2R1', 'T2C2R2'],
    5901: ['T5C1R1', 'T5C1R2', 'T5C2R1', 'T5C2R2', 'T6C1R1', 'T6C1R2', 'T6C2R1', 'T6C2R2']
}

BASE_CHARGE_PROFILES = {  # map of base profiles to use for each pair of specimens - FC = fast charge, SC = slow charge
    'C0':   {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T1C1': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T1C2': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T2C1': {'FC': '3C0_charge_60_knee',         'SC': 'recovery_charge'},
    'T2C2': {'FC': '3C0_charge_60_knee',         'SC': 'recovery_charge'},
    'T2C3': {'FC': '3C0_charge_60_knee',         'SC': 'recovery_charge'},
    'T3C1': {'FC': '2C2_charge_no_knee',         'SC': 'recovery_charge'},
    'T4C1': {'FC': '3C0_charge_no_knee',         'SC': 'recovery_charge'},
    'T4C2': {'FC': '3C0_charge_80_knee',         'SC': 'recovery_charge'},
    'T5C1': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T5C2': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T6C1': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T6C2': {'FC': '2C2_charge_60_knee',         'SC': 'recovery_charge'},
    'T7C1': {'FC': '1C5_charge_no_knee',         'SC': 'recovery_charge'},
    'T7C2': {'FC': '1C0_charge_no_knee',         'SC': 'recovery_charge'},
    'T7C3': {'FC': '0C5_charge_no_knee',         'SC': 'recovery_charge'},
    'T8C1': {'FC': '1C0_charge_no_knee_90_soc',  'SC': 'recovery_charge_90_soc'},
    'T9C1': {'FC': '2C2_charge_60_knee_lowside_taper', 'SC': 'recovery_charge'}
}

DISCHARGE_DEPTHS = {  # map of DODs to use for each pair of specimens - EX = extended, ST = standard
    'C0':   {'EX': 0.85, 'ST': 0.68},
    'T1C1': {'EX': 0.85, 'ST': 0.68},
    'T1C2': {'EX': 0.85, 'ST': 0.68},
    'T2C1': {'EX': 0.85, 'ST': 0.68},
    'T2C2': {'EX': 0.85, 'ST': 0.68},
    'T2C3': {'EX': 0.85, 'ST': 0.68},
    'T3C1': {'EX': 0.85, 'ST': 0.68},
    'T4C1': {'EX': 0.85, 'ST': 0.68},
    'T4C2': {'EX': 0.85, 'ST': 0.68},
    'T5C1': {'EX': 0.85, 'ST': 0.68},
    'T5C2': {'EX': 0.85, 'ST': 0.68},
    'T6C1': {'EX': 0.95, 'ST': 0.75},
    'T6C2': {'EX': 0.75, 'ST': 0.61},
    'T7C1': {'EX': 0.85, 'ST': 0.68},
    'T7C2': {'EX': 0.85, 'ST': 0.68},
    'T7C3': {'EX': 0.85, 'ST': 0.68},
    'T8C1': {'EX': 0.85, 'ST': 0.68},
    'T9C1': {'EX': 0.85, 'ST': 0.68}
}

SLOW_CHARGE_FREQUENCIES = {     #how often to use a slow recovery charge instead of the fast charge
    'C0': 0.1,
    'T1C1': 0.1,
    'T1C2': 0.1,
    'T2C1': 0.1,
    'T2C2': 0.1,
    'T2C3': 0.1,
    'T3C1': 0.1,
    'T4C1': 0.1,
    'T4C2': 0.1,
    'T5C1': 0.0,
    'T5C2': 0.25,
    'T6C1': 0.1,
    'T6C2': 0.1,
    'T7C1': 0.1,
    'T7C2': 0.1,
    'T7C3': 0.1,
    'T8C1': 0.1,
    'T9C1': 0.1
}

EX_DISCHARGE_FREQUENCY = 0.01  #how often extended discharge is used compared to standard discharge

CHARGE_TAPER_STEP = 10  #this is the step in the fast charge profiles where cutoff current is used
DISCHARGE_VARIED_STEP = 6  #this is the step in discharge profiles where the time is varied (represents transit inbound)

DISCHARGE_POWER_VARIED_STEP = { #power in W during varied part of discharge profile
    'EX': 22,
    'ST': 19
}

DISCHARGE_FIXED_WH = {  #Wh used by all steps other than variable one
    'EX': 4.286,
    'ST': 3.379
}

DISCHARGE_PROFILES =  {
    'EX': 'ex_discharge.xml',
    'ST': 'st_discharge.xml'
}

P45B_NOM_WH = 16.2  #nominal energy in Wh for P45B cells
P45B_NOM_AH = 4.5  #nominal capacity in Ah for P45B cells
P45B_NOM_V = P45B_NOM_WH / P45B_NOM_AH  #nominal voltage in V for P45B cells