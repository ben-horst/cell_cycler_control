from cell_cycler import CellCycler
import json

cycler = CellCycler()

test_path = 'test_profiles/P45B_cycle_test_2023.json'
with open(test_path, 'r') as json_file:
    test_info = json.load(json_file)


#throughput_30soc = input("enter Ah for 30% SOC phase: ")
#throughput_0soc = input("enter Ah for 0% SOC (2.65 V) phase: ")

#updated_params = cycler.update_test_profile_params(profile, )

