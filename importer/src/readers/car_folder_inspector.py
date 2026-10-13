"""Strict, read-only normalization of a user-approved Assetto Corsa car folder.

This is an inspection preview. Do not confuse raw LUT torque data with measured
engine power, predicted acceleration, or recommended shift points.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .ac_folder_reader import CarFolderReadError, parse_ini_sections, read_car_folder

MAX_LUT_RECORDS = 500
ALLOWED_DRIVE = {"RWD", "FWD", "AWD", "4WD"}


def _number(raw: str | None, field: str, *, positive: bool = False) -> float | None:
    if raw is None or not raw.strip():
        return None
    try:
        number = float(raw.strip())
    except ValueError as exc:
        raise CarFolderReadError(f"{field}: expected a number.") from exc
    if not math.isfinite(number) or (positive and number <= 0):
        raise CarFolderReadError(f"{field}: invalid numeric value.")
    return number


def _integer(raw: str | None, field: str, *, low: int, high: int) -> int | None:
    number = _number(raw, field)
    if number is None:
        return None
    if not number.is_integer() or not low <= number <= high:
        raise CarFolderReadError(f"{field}: out of accepted range.")
    return int(number)


def parse_raw_lut(text: str) -> list[list[float | int]]:
    """Keep raw RPM/ordinate pairs, without HP/torque conversion or extrapolation."""
    result: list[list[float | int]] = []
    previous_rpm = 0
    for line in text.splitlines():
        stripped = line.split(";", 1)[0].strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"\s*([0-9]+)\s*\|\s*([+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))\s*", stripped)
        if not match:
            raise CarFolderReadError("power.lut: malformed row.")
        rpm = int(match.group(1))
        ordinate = float(match.group(2))
        if not 0 < rpm <= 30000 or rpm <= previous_rpm or not math.isfinite(ordinate):
            raise CarFolderReadError("power.lut: RPM must increase strictly and values must be finite.")
        if len(result) >= MAX_LUT_RECORDS:
            raise CarFolderReadError("power.lut: too many entries.")
        result.append([rpm, ordinate])
        previous_rpm = rpm
    return result


def inspect_car_folder(folder: str | Path) -> dict:
    """Read four fixed filenames only. Return validated values, never write or plot."""
    files = read_car_folder(folder)
    car = parse_ini_sections(files["car.ini"])
    drivetrain = parse_ini_sections(files["drivetrain.ini"]) if "drivetrain.ini" in files else {}
    engine = parse_ini_sections(files["engine.ini"]) if "engine.ini" in files else {}

    name = car.get("INFO", {}).get("SCREEN_NAME", "").strip()
    words = name.split()
    if len(words) < 2:
        raise CarFolderReadError("car.ini [INFO] SCREEN_NAME must contain make and model.")
    manufacturer, model = words[0], " ".join(words[1:])
    basic = car.get("BASIC", {})
    controls = car.get("CONTROLS", {})
    fuel = car.get("FUEL", {})
    traction = drivetrain.get("TRACTION", {})
    gears = drivetrain.get("GEARS", {})
    engine_data = engine.get("ENGINE_DATA", {})

    mass = _number(basic.get("TOTALMASS"), "TOTALMASS", positive=True)
    if mass is None:
        raise CarFolderReadError("car.ini [BASIC] TOTALMASS is required.")
    drive = traction.get("TYPE", "").upper() or None
    if drive is not None and drive not in ALLOWED_DRIVE:
        raise CarFolderReadError("drivetrain.ini [TRACTION] TYPE is not recognized.")
    count = _integer(gears.get("COUNT"), "GEARS COUNT", low=1, high=12)
    ratios = []
    if count is not None:
        for i in range(1, count + 1):
            ratio = _number(gears.get(f"GEAR_{i}"), f"GEAR_{i}", positive=True)
            if ratio is None:
                raise CarFolderReadError(f"drivetrain.ini: missing GEAR_{i} for COUNT={count}.")
            ratios.append(ratio)

    curve_file = engine.get("HEADER", {}).get("POWER_CURVE", "").strip()
    if curve_file and curve_file.casefold() != "power.lut":
        raise CarFolderReadError("engine.ini refers to a non-allowlisted LUT; no external path is opened.")
    lut_data = parse_raw_lut(files["power.lut"]) if "power.lut" in files else []
    if curve_file and "power.lut" not in files:
        raise CarFolderReadError("engine.ini refers to power.lut, but the file is missing.")

    limiter = _integer(engine_data.get("LIMITER"), "LIMITER", low=0, high=30000)
    # A zero LIMITER means no rev limiter, not zero RPM.
    return {
        "manufacturer": manufacturer,
        "model": model,
        "mass": mass,
        "steer_lock": _number(controls.get("STEER_LOCK"), "STEER_LOCK", positive=True),
        "max_fuel": _number(fuel.get("MAX_FUEL"), "MAX_FUEL", positive=True),
        "drivetrain": drive,
        "gears": count,
        "gear_ratios": ratios,
        "final_drive": _number(gears.get("FINAL"), "FINAL", positive=True),
        "limiter": limiter or None,
        "power_curve": curve_file or None,
        "power_data": lut_data,
        "max_power": None,
        "max_torque": None,
        "source_files": list(files),
        "power_data_origin": "raw AC LUT ordinate; not converted to HP",
        "inspection_only": True,
    }
