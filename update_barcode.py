580103
from barcode_manager import BarcodeManager

bcm = BarcodeManager()

chlcode = input('scan channel code: ')
old_barcode = bcm.barcodes_from_chlcodes(chlcode)
print(f'current cell in this position: {old_barcode}')
new_barcode = input('scan new barcode (or press enter to cancel): ')
if not new_barcode == '':
    bcm.update_barcode(chlcode, new_barcode)
print(f'successfully updated {bcm.barcodes_from_chlcodes(chlcode)} in position {chlcode}')