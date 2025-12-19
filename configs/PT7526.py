AVAILABLE_BANKS = [5801, 5902]
BANK_CHARGE_TEMPS = { 
    5801: 55,
    5902: 40
}

DISCHARGE_TEMP = 40

CHANNELS_PER_BANK = {   #active channel numbers for each bank
    5801: [580105, 580106],
    5902: [590201, 590202, 590203, 590204, 590205, 590206]
}

SPECIMENS_PER_BANK = {  # specimen IDs for each bank (placeholder IDs; update later)
    5801: ['E4R1', 'E4R2'],
    5902: ['E1R1', 'E1R2', 'E2R1', 'E2R2', 'E3R1', 'E3R2']
}

BASE_CHARGE_PROFILES = {  # map of base profiles to use for each pair of specimens - FC = fast charge, SC = slow charge
    'E1R1': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'},
    'E1R2': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'},
    'E2R1': {'FC': '3C0_charge_60_knee',                   'SC': 'recovery_charge'},
    'E2R2': {'FC': '3C0_charge_60_knee',                   'SC': 'recovery_charge'},
    'E3R1': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'},
    'E3R2': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'},
    'E4R1': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'},
    'E4R2': {'FC': '2C2_charge_60_knee',                   'SC': 'recovery_charge'}
}

DISCHARGE_DEPTHS = {  # map of DODs to use for each pair of specimens - EX = extended, ST = standard
    'E1R1': {'EX': 0.74, 'ST': 0.60},
    'E1R2': {'EX': 0.74, 'ST': 0.60},
    'E2R1': {'EX': 0.74, 'ST': 0.60},
    'E2R2': {'EX': 0.74, 'ST': 0.60},
    'E3R1': {'EX': 0.85, 'ST': 0.68},
    'E3R2': {'EX': 0.85, 'ST': 0.68},
    'E4R1': {'EX': 0.74, 'ST': 0.60},
    'E4R2': {'EX': 0.74, 'ST': 0.60}
}

SLOW_CHARGE_FREQUENCIES = {     #how often to use a slow recovery charge instead of the fast charge
    'E1R1': 0.1,
    'E1R2': 0.1,
    'E2R1': 0.1,
    'E2R2': 0.1,
    'E3R1': 0.1,
    'E3R2': 0.1,
    'E4R1': 0.1,
    'E4R2': 0.1
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

H52A_NOM_WH = 18.72  # nominal energy in Wh for H52A cells
H52A_NOM_AH = 5.2    # nominal capacity in Ah for H52A cells
H52A_NOM_V = H52A_NOM_WH / H52A_NOM_AH  # nominal voltage in V for H52A cells

#specs for OCV extraction profiles
OCV_CHARGE_PROFILE = 'H52_OCV_V1.0_chg.xml'
OCV_DISCHARGE_PROFILE = 'H52_OCV_V1.0_dchg.xml'
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