import os
from typing import List, Tuple

import configs.PT5801 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT5801 import CycleManager
from core.progress_report_PT5801 import ProgressReporter


def _resolve_profile_folder(parent_folder: str) -> str:
    folders = [
        os.path.join(parent_folder, d)
        for d in os.listdir(parent_folder)
        if os.path.isdir(os.path.join(parent_folder, d))
    ]
    if not folders:
        raise ValueError("No folders found in the parent folder.")
    return max(folders, key=os.path.getmtime)


def _filter_skips(specimens: List[str], channels: List[int], specimens_to_skip_csv: str) -> Tuple[List[str], List[int]]:
    if not specimens_to_skip_csv:
        return specimens, channels
    specimens_to_skip = [specimen.strip() for specimen in specimens_to_skip_csv.split(",") if specimen.strip()]
    channels_to_skip = [channels[specimens.index(specimen)] for specimen in specimens_to_skip if specimen in specimens]
    specimens = [specimen for specimen in specimens if specimen not in specimens_to_skip]
    channels = [channel for channel in channels if channel not in channels_to_skip]
    return specimens, channels


def run_cycles(
    bank_request: int,
    cycles_to_complete: int,
    specimens_to_skip_csv: str = "",
):
    # Constants copied from runner_PT5801_cycles.py
    profile_parent_folder = "G:/My Drive/Cell Test Profiles/Cycles/PT5801_tuned_profiles"
    savepath = "G:/My Drive/Cell Test Data/PT5801/Cycles"
    test_title = "PT5801_Cycles"

    cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_P45B_1C_4C.xml"
    cqt_savepath = "G:/My Drive/Cell Test Data/PT5801/CQTs"
    cqt_temp = 25

    strg_profile = "G:/My Drive/Cell Test Profiles/Utilities/storage_charge_P45B.xml"
    strg_savepath = "G:/My Drive/Cell Test Data/PT5801/Storage_Charges"
    strg_temp = 20
    strg_filename = "storage_charge"

    if bank_request not in CONFIG.AVAILABLE_BANKS:
        raise ValueError(f"Invalid bank number. Available banks are {CONFIG.AVAILABLE_BANKS}.")
    if cycles_to_complete <= 0:
        raise ValueError("Invalid number of cycles. Must be greater than 0.")

    profile_folder = _resolve_profile_folder(profile_parent_folder)
    print(f"Folder for profiles: {profile_folder}")

    channels = CONFIG.CHANNELS_PER_BANK[bank_request][:]
    specimens = CONFIG.SPECIMENS_PER_BANK[bank_request][:]
    print(f"All specimens in bank {bank_request}: {specimens}")

    specimens, channels = _filter_skips(specimens, channels, specimens_to_skip_csv)
    print(f"Active specimens after skip filter: {specimens}")
    print(f"Active channels after skip filter: {channels}")

    cycle_manager = CycleManager()
    print(f"\nSpecimen cycle counts from cycle tracker json file for bank {bank_request}:")
    print("---------------------------------------------------------------")
    print("Specimen ID:\tlast cycle number\tlast cycle direction")

    cqt_filenames = []
    for specimen in specimens:
        cycle, direction = cycle_manager.get_last_cycle(specimen)
        cqt_filenames.append(f"{specimen}_CQT_after_{cycle}_cycles")
        print(f"{specimen}\t\t\t{cycle}\t\t\t{direction}")

    # Check profile files exist
    suffixes = ["FC", "SC", "EX", "ST"]
    for specimen in specimens:
        for suffix in suffixes:
            profile_name = f"{specimen}_{suffix}.xml"
            profile_path = f"{profile_folder}/{profile_name}"
            if not os.path.isfile(profile_path):
                raise ValueError(f"Profile {profile_name} not found in {profile_folder}.")
    print("\nAll profiles found for all specimens!\n")

    test_runner = TestRunner(channels, test_title, interactive=False)
    barcodes = test_runner.barcodes

    # Connection quality check
    print("Setting temperature for cell connection quality test...")
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=30, verbose=False)
    print("Waiting for any tests to complete")
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=60, verbose=False)
    test_runner.start_tests(channels, cqt_profile, cqt_savepath, cqt_filenames, verbose=False)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4, verbose=False)
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, "CQT", increment=False)
    print("\nCQT successful! Bringing cells to target charge temp...")

    cycles_completed = 0
    while cycles_completed < cycles_to_complete:
        # Charge
        test_runner.bring_all_cells_to_temp_and_block_until_complete(
            temp=CONFIG.BANK_CHARGE_TEMPS[bank_request], timeout_mins=60, verbose=False
        )
        print(f"Starting charge {cycles_completed + 1}/{cycles_to_complete} on bank {bank_request}...")
        print("---------------------------------------------------------------")
        print("Specimen ID:\tChannel ID\tCycle\tCharge Type\tStart Result")
        for specimen in specimens:
            last_cycle, direction = cycle_manager.get_last_cycle(specimen)
            current_cycle = last_cycle + 1
            charge_type = cycle_manager.get_charge_type(current_cycle, specimen)
            charge_profile = f"{specimen}_{charge_type}.xml"
            charge_profile_path = f"{profile_folder}/{charge_profile}"
            channel = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]
            charge_filename = f"{specimen}_cycle_{current_cycle}_chg"
            result = test_runner.start_tests([channel], charge_profile_path, savepath, charge_filename, verbose=False)
            print(f"{specimen}\t\t{channel}\t\t{current_cycle}\t{charge_type}\t\t{result[0]}")
        test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=300, verbose=False)
        print(f"Charge event {cycles_completed + 1}/{cycles_to_complete} complete for all specimens in bank {bank_request}")
        for specimen in specimens:
            cycle_manager.update_cycle_tracker(specimen, "CHG", increment=False)

        # Discharge
        test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=CONFIG.DISCHARGE_TEMP, timeout_mins=60, verbose=False)
        print(f"Starting discharge {cycles_completed + 1}/{cycles_to_complete} on bank {bank_request}...")
        print("---------------------------------------------------------------")
        print("Specimen ID:\tChannel ID\tCycle\tDischarge Type\tStart Result")
        for specimen in specimens:
            last_cycle, direction = cycle_manager.get_last_cycle(specimen)
            current_cycle = last_cycle + 1
            discharge_type = cycle_manager.get_discharge_type(current_cycle, specimen)
            discharge_profile = f"{specimen}_{discharge_type}.xml"
            discharge_profile_path = f"{profile_folder}/{discharge_profile}"
            channel = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]
            discharge_filename = f"{specimen}_cycle_{current_cycle}_dchg"
            result = test_runner.start_tests([channel], discharge_profile_path, savepath, discharge_filename, verbose=False)
            print(f"{specimen}\t\t{channel}\t\t{current_cycle}\t{discharge_type}\t\t{result[0]}")
        test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=120, verbose=False)
        print(f"Discharge event {cycles_completed + 1}/{cycles_to_complete} complete for all specimens in bank {bank_request}")
        for specimen in specimens:
            cycle_manager.update_cycle_tracker(specimen, "DCHG", increment=True)
        cycles_completed += 1
        print(f"Completed {cycles_completed} cycles out of {cycles_to_complete} on bank {bank_request}")

    print("All cycles complete!")

    # Storage charge
    print("Setting temperature for storage charge...")
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=strg_temp, timeout_mins=30, verbose=False)
    test_runner.start_tests(channels, strg_profile, strg_savepath, strg_filename, verbose=False)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=120, verbose=False)
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, "STRG", increment=False)
    print("\nStorage Charge Complete.\n")

    print("\nSpecimen status after tests.\n")
    print("---------------------------------------------------------------")
    summary_table = "Specimen\tBarcode\t\tChannel\t\tLast Cycle\tLast Event\n"
    for specimen in specimens:
        last_cycle, last_event = cycle_manager.get_last_cycle(specimen)
        chan = CONFIG.CHANNELS_PER_BANK[bank_request][specimens.index(specimen)]
        barcode = barcodes[specimens.index(specimen)]
        summary_table += f"{specimen}\t\t{barcode}\t{chan}\t\t{last_cycle}\t\t{last_event}\n"

    print(summary_table)

    progress_reporter = ProgressReporter()
    progress_reporter.generate_progress_report_csv()
    progress_reporter.save_copy_cycle_tracker_json()

    message = f"""{cycles_to_complete} cycles completed successfully for cycle accumulation of PT-5801. All data saved to {savepath}.
                       
                       Bank tested: {bank_request}
                       
                       Specimens tested: {specimens}
                       
                       Cells Tested: {barcodes}
                       
                       {summary_table}"""

    test_runner.send_email(f"{test_title} Complete", message)
    print("Test complete. Exiting.")


