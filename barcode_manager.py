import json

class BarcodeManager():
    def __init__(self,filepath='barcode_database.json'):
        self.filepath = filepath

    def barcodes_from_chlcodes(self, chlcodes):
        """takes a list of channel codes in the for 580206 and returns a list of corresponding barcodes"""

        with open(self.filepath, 'r') as json_file:
            database = json.load(json_file)
            barcodes = []
            for chlcode in chlcodes:
                chlcode_str = str(chlcode)
                barcodes.append(database.get(chlcode_str))
        return barcodes
    
    def update_barcode(self, chlcode, barcode):
        """takes in a channel code and barcode and updates the database accordingly"""
        with open(self.filepath, 'r') as json_file:
            database = json.load(json_file)
        chlcode_str = str(chlcode)
        if chlcode_str in database.keys():
            database.update({chlcode_str: barcode})
            with open("barcode_database.json", "w") as json_file: 
                json.dump(database, json_file)
