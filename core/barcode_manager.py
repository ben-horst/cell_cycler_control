import json

class BarcodeManager():
    def __init__(self,filepath='./configs/barcode_database.json'):
        self.filepath = filepath
        self.minimum_barcode_length = 7

    def barcodes_from_chlcodes(self, chlcodes):
        """takes a list of channel codes in the for 580206 and returns a list of corresponding barcodes
        also accepts a single value in either int or string format"""

        with open(self.filepath, 'r') as json_file:
            database = json.load(json_file)
            if isinstance(chlcodes, list):
                barcodes = []
                for chlcode in chlcodes:
                    chlcode_str = str(chlcode)
                    barcodes.append(database.get(chlcode_str))
                if len(barcodes) == 0:
                    raise Exception("channel codes not found")
            else:
                chlcode_str = str(chlcodes)
                barcodes = database.get(chlcode_str)
                if barcodes is None:
                    raise Exception("invalid channel code")
        return barcodes
    
    def update_barcode(self, chlcode, barcode):
        """takes in a channel code and barcode and updates the database accordingly"""
        if len(str(barcode)) < self.minimum_barcode_length:
            raise Exception(f"barcode must be at least {self.minimum_barcode_length} digits")
        with open(self.filepath, 'r') as json_file:
            database = json.load(json_file)
        chlcode_str = str(chlcode)
        if chlcode_str in database.keys():
            database.update({chlcode_str: barcode})
            with open("barcode_database.json", "w") as json_file: 
                json.dump(database, json_file)
        else:
            raise Exception("invalid channel code")
        