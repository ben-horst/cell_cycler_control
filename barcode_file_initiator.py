import json

barcodes = {}

devs = [27,52,58,59]
subdevs = [1,2]
chls = [1,2,3,4,5,6,7,8]

for dev in devs:
    for subdev in subdevs:
        for chl in chls:
            chlcode = str(dev*10000 + subdev*100 + chl)
            barcodes.update({chlcode: 'ABC123'})

with open("barcode_database.json", "w") as file: 
    json.dump(barcodes, file)
