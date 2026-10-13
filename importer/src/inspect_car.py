"""Opt-in, read-only AC folder inspection.

Run from the DDL repository root:
    python -m importer.src.inspect_car --car-dir "C:/.../content/cars/<car>/data"
No files are modified, exported, or uploaded. The installed AC car is never scanned.
"""

from __future__ import annotations

import argparse
import json

from .readers.ac_folder_reader import CarFolderReadError
from .readers.car_folder_inspector import inspect_car_folder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect exactly four allowlisted AC files, read-only.")
    parser.add_argument("--car-dir", required=True, help="Explicit path to one AC car's data folder.")
    parser.add_argument("--json", action="store_true", help="Print normalized raw data to standard output.")
    args = parser.parse_args(argv)

    try:
        record = inspect_car_folder(args.car_dir)
    except CarFolderReadError as exc:
        parser.exit(2, "DDL inspection refused: " + str(exc) + "\n")
    except OSError:
        parser.exit(2, "DDL inspection refused: local folder is not readable.\n")

    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False))
    else:
        print("DDL — LOCAL READ-ONLY VEHICLE INSPECTION")
        print("Vehicle:", record["manufacturer"], record["model"])
        print("Mass (AC data):", record["mass"], "kg")
        print("Drivetrain:", record["drivetrain"] or "unknown")
        print("Forward gears:", record["gears"] or "unknown")
        print("Limiter:", record["limiter"] if record["limiter"] is not None else "unknown")
        print("Raw LUT points:", len(record["power_data"]))
        print("Calculated performance: not available; no values inferred.")
        print("No files written. No network access.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
