from cell_cycler import CellCycler
import xml.etree.ElementTree as ET

#cycler = CellCycler()
profile = "C:/Users/cell.test/Documents/Current Test Profiles/Cycle Tests/P45_cycle_test_V1.0.xml"
savepath = "C:/Users/cell.test/Documents/BackupData"

#throughput_30soc = int(float(input("enter Ah for 30% SOC phase: ")) * 1000 * 3600)      #data is stored in mAs
#throughput_0soc = int(float(input("enter Ah for 0% SOC (2.65 V) phase: ")) * 1000 * 3600)
#cycle_number = input("enter cycle number: ")
#testname = f'P45B_cycle_{cycle_number}'
#channels = [580201, 580202]

prsr = ET.XMLParser(encoding="utf-8")
tree = ET.parse(profile, parser=prsr)
root = tree.getroot()

for match in root.iter('Scale'):
    print(match.get('Value'))

"""
#step8 in the profile is the 30%soc discharge
for step8 in root.iter('Step8'):
    for cap in step8.iter('Cap'):
        newcap = str(throughput_30soc)
        cap.set('Value', newcap)

#step19 in the profile is the 0%soc discharge
for step19 in root.iter('Step19'):
    for cap in step19.iter('Cap'):
        newcap = str(throughput_0soc)
        cap.set('Value', newcap)
"""

#tree.write(profile)

#print(cycler.start_channels(channels, profile, savepath, testname))