import os
from typing import List, Iterable, Tuple, Dict, Any, Optional

import configs.PT7526 as CONFIG
from core.test_runner import TestRunner
from core.cycle_manager_PT7526 import CycleManager


def _parse_banks(banks_input: Iterable[Any]) -> List[int]:
    """Normalize banks input to a list of valid bank IDs."""
    if isinstance(banks_input, str):
        text = banks_input.strip()
        if text.upper() == "ALL":
            return list(CONFIG.AVAILABLE_BANKS)
        parts = [p.strip() for p in text.split(",") if p.strip()]
        banks = [int(p) for p in parts]
    elif isinstance(banks_input, Iterable):
        banks = [int(b) for b in banks_input]
    else:
        raise ValueError("banks_input must be 'ALL', a CSV string, or an iterable of bank IDs.")

    invalid = [b for b in banks if b not in CONFIG.AVAILABLE_BANKS]
    if invalid:
        raise ValueError(f"Invalid bank(s) {invalid}. Available banks are {CONFIG.AVAILABLE_BANKS}.")
    if not banks:
        raise ValueError("No banks specified after parsing.")
    return banks


def _build_pairs(active_banks: List[int]) -> List[Tuple[int, str]]:
    """Return list of (channel, specimen) tuples for the selected banks, validating mapping sizes."""
    pairs: List[Tuple[int, str]] = []
    for bank in active_banks:
        bank_channels = CONFIG.CHANNELS_PER_BANK[bank]
        bank_specimens = CONFIG.SPECIMENS_PER_BANK[bank]
        if len(bank_channels) != len(bank_specimens):
            raise ValueError(f"Bank {bank} has {len(bank_channels)} channels but {len(bank_specimens)} specimens.")
        pairs.extend(zip(bank_channels, bank_specimens))
    return pairs


def _filter_pairs_by_skip(pairs: List[Tuple[int, str]], specimens_to_skip_csv: str) -> List[Tuple[int, str]]:
    if not specimens_to_skip_csv:
        return pairs
    to_skip_norm = {s.strip().upper() for s in specimens_to_skip_csv.split(",") if s.strip()}
    print(f"specimens to skip: {sorted(to_skip_norm)}")
    return [(ch, sp) for (ch, sp) in pairs if sp.upper() not in to_skip_norm]


def _ensure_profiles_exist(profile_paths: List[str]):
    missing = [p for p in profile_paths if not os.path.isfile(p)]
    if missing:
        raise FileNotFoundError(f"Profile file(s) not found: {missing}")


def run_rpt(
    banks_input: Iterable[Any] | str,
    specimens_to_skip_csv: str = "",
    temps: Optional[List[int]] = None,
    cqt_temp: int = 25,
    chiller_timeout_mins: int = 60,
    cqt_timeout_mins: int = 30,
    rpt_timeout_mins: int = 60 * 48,
    test_title: str = "PT7526_RPTs",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Execute the PT-7526 RPT sequence across selected banks.

    Args:
        banks_input: 'ALL', CSV string like '2701, 5801', or iterable of bank IDs
        specimens_to_skip_csv: comma-separated list of specimen IDs to skip
        temps: list of RPT temperatures (defaults to [20, 35, 50])
        cqt_temp: temperature for CQT
        chiller_timeout_mins: timeout for temperature set/soak operations
        cqt_timeout_mins: timeout for CQT test completion
        rpt_timeout_mins: timeout for each RPT run per temperature
        test_title: title used in email/logging
        verbose: print additional progress logs

    Returns:
        Summary dictionary of the run.
    """
    # Paths
    profile = "G:/My Drive/Cell Test Profiles/RPTs/H52_RPT_V1.2.xml"
    savepath = "G:/My Drive/Cell Test Data/PT7526/RPTs"
    cqt_profile = "G:/My Drive/Cell Test Profiles/Utilities/CQT_H52_1C_4C.xml"
    cqt_savepath = "G:/My Drive/Cell Test Data/PT7526/CQTs"

    # Defaults
    temps = temps or [20, 35, 50]

    # Parse and validate inputs
    active_banks = _parse_banks(banks_input)
    pairs = _build_pairs(active_banks)
    if verbose:
        print(f"All specimens in banks {active_banks}: {[sp for _, sp in pairs]}")

    pairs = _filter_pairs_by_skip(pairs, specimens_to_skip_csv)
    if not pairs:
        raise ValueError("No specimens remain after skipping. Aborting.")

    channels = [ch for (ch, _) in pairs]
    specimens = [sp for (_, sp) in pairs]
    cycle_manager = CycleManager()

    # Filenames use cycle count
    print("\nSpecimen cycle counts from cycle tracker json file:")
    print("Specimen ID:\tlast cycle number\tlast cycle direction")
    filenames = []
    for specimen in specimens:
        cycle, direction = cycle_manager.get_last_cycle(specimen)
        filenames.append(f"{specimen}_RPT_after_{cycle}_cycles")
        print(f"{specimen}\t\t\t{cycle}\t\t\t{direction}")

    # Validate profiles exist (fail fast)
    _ensure_profiles_exist([profile, cqt_profile])

    # Execute tests
    test_runner = TestRunner(channels, test_title, interactive=False)
    barcodes = test_runner.barcodes

    # CQT
    print("Setting temperature for cell connection quality test...")
    test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=cqt_temp, timeout_mins=cqt_timeout_mins, verbose=verbose)
    test_runner.start_tests(channels, cqt_profile, cqt_savepath, filenames, verbose=verbose)
    test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=4, verbose=verbose)
    for specimen in specimens:
        cycle_manager.update_cycle_tracker(specimen, "CQT", increment=False)

    # RPTs across temps
    for temp in temps:
        test_runner.bring_all_cells_to_temp_and_block_until_complete(temp=temp, timeout_mins=chiller_timeout_mins, verbose=verbose)
        filenames_with_temps = [f"{filename}_at_{temp}degC" for filename in filenames]
        test_runner.start_tests(channels, profile, savepath, filenames_with_temps, verbose=verbose)
        test_runner.wait_for_all_channels_to_finish_and_block_until_complete(timeout_mins=rpt_timeout_mins, verbose=verbose)
        for specimen in specimens:
            cycle_manager.update_cycle_tracker(specimen, "RPT", increment=False)

    test_runner.send_email(
        f"{test_title} Test Complete",
        f"""All tests completed successfully for multitemp RPT for PT-7526.
                       
                       RPT temperatures: {temps} degC
                       
                       Banks tested: {active_banks}
                       
                       Specimens tested: {specimens}
                       
                       Cells Tested: {barcodes}""",
    )

    return {
        "banks": active_banks,
        "specimens": specimens,
        "barcodes": barcodes,
        "temps": temps,
        "savepath": savepath,
        "cqt_savepath": cqt_savepath,
        "rpt_profile": profile,
        "cqt_profile": cqt_profile,
        "title": test_title,
    }


if __name__ == "__main__":
    # Simple CLI for local testing
    import argparse

    parser = argparse.ArgumentParser(description="Run PT7526 RPTs")
    parser.add_argument("--banks", required=True, help="ALL or CSV of bank IDs, e.g. '2701,5801'")
    parser.add_argument("--skip", default="", help="CSV of specimen IDs to skip")
    parser.add_argument("--temps", default="", help="CSV of temps, e.g. '20,35,50'")
    parser.add_argument("--cqt_temp", type=int, default=25)
    parser.add_argument("--chiller_timeout", type=int, default=60)
    parser.add_argument("--cqt_timeout", type=int, default=30)
    parser.add_argument("--rpt_timeout", type=int, default=60 * 48)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    temps_list = None
    if args.temps.strip():
        temps_list = [int(t.strip()) for t in args.temps.split(",") if t.strip()]

    summary = run_rpt(
        banks_input=args.banks,
        specimens_to_skip_csv=args.skip,
        temps=temps_list,
        cqt_temp=args.cqt_temp,
        chiller_timeout_mins=args.chiller_timeout,
        cqt_timeout_mins=args.cqt_timeout,
        rpt_timeout_mins=args.rpt_timeout,
        verbose=not args.quiet,
    )
    print("Summary:", summary)

