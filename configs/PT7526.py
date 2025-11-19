AVAILABLE_BANKS = [5801, 5902]
#  need to be updated 
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
    5801: [580105, 580106],
    5902: [590201, 590203, 590204, 590205, 590206, 590208] #  Skipped 590207 
}

SPECIMENS_PER_BANK = {  # specimen IDs for each bank (placeholder IDs; update later)
    5801: ['SPEC_5801_A', 'SPEC_5801_B'],
    5902: ['SPEC_5902_1', 'SPEC_5902_2', 'SPEC_5902_3', 'SPEC_5902_4', 'SPEC_5902_5', 'SPEC_5902_6']
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

#specs for OCV extraction profiles
OCV_CHARGE_PROFILE = 'P45_OCV_V1.0_chg.xml'
OCV_DISCHARGE_PROFILE = 'P45_OCV_V1.0_dchg.xml'
OCV_CHARGE_STEPS = {    #dist in the format: step#: SOC, where SOC is the % charged/discharged in that step
    'Step4': 100,     #discharge from 100% to 0%
    'Step6': 3,       #0-3%, 3-6%
    'Step9': 4,       #6-10%
    'Step11': 5,      #15:5:30%
    'Step14': 5,      #35:5:90%
    'Step17': 3,      #90-93%, 93-96%
    'Step20': 4       #96-100%
}
OCV_DISCHARGE_STEPS = {    #dist in the format: step#: SOC, where SOC is the % charged/discharged in that step
    'Step4': 4,       #96-100%
    'Step6': 3,       #90-93%, 93-96%
    'Step9': 5,       #35:5:90%
    'Step12': 5,      #15:5:30%
    'Step15': 5,      #15-10%
    'Step17': 4,      #6-10%
    'Step19': 3       #0-3%, 3-6
}