AVAILABLE_BANKS = [2701, 2702, 5201, 5202, 5801, 5901]

CHANNELS_PER_BANK = {   #active channel numbers for each bank
    2701: [270101, 270102, 270103, 270104],
    2702: [270201, 270202, 270203, 270204],
    5201: [520101, 520102, 520103, 520104],
    5202: [520201, 520202, 520203, 520204, 520205, 520206],
    5801: [580101, 580102, 580103, 580104],
    5901: [590101, 590102, 590103, 590104, 590105, 590106, 590107, 590108]
}

SPECIMENS_PER_BANK = {  #specimen IDs for each bank
    2701: ['T1C2R1', 'T1C2R2', 'T2C2R1', 'T2C2R2'],
    2702: ['C0R1',   'C0R2',   'T3C1R1', 'T3C1R2'],
    5201: ['T1C1R1', 'T1C1R2', 'T2C1R1', 'T2C1R2'],
    5202: ['T2C4R1', 'T2C4R2', 'T4C1R1', 'T4C1R2', 'T4C2R1', 'T4C2R2'],
    5801: ['T1C3R1', 'T1C3R2', 'T2C3R1', 'T2C3R2'],
    5901: ['T5C1R1', 'T5C1R2', 'T5C2R1', 'T5C2R2', 'T6C1R1', 'T6C1R2', 'T6C2R1', 'T6C2R2']
}