from barcode_manager import BarcodeManager

bcm = BarcodeManager()
chlcodes = [270105]

print(bcm.barcodes_from_chlcodes(chlcodes))
bcm.update_barcode(270105,'yayitworked')
print(bcm.barcodes_from_chlcodes(chlcodes))