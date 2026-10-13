"""Read ONLY the four supported, explicitly selected AC physics files.

This module is a staging boundary, not a physics model or a disk exporter.
It never follows symlinks, opens paths supplied by INI content, or writes files.
"""

from __future__ import annotations

import configparser
from pathlib import Path

MAX_INPUT_BYTES = 1024 * 1024
INPUT_NAMES = ("car.ini", "drivetrain.ini", "engine.ini", "power.lut")


class CarFolderReadError(ValueError):
    """The explicitly selected car folder cannot be read safely."""


def _read_optional_file(directory: Path, name: str, *, required: bool = False) -> str | None:
    if name not in INPUT_NAMES:
        raise CarFolderReadError("Unrecognized AC file name.")
    source = directory / name
    if source.is_symlink():
        raise CarFolderReadError(f"{name}: linked files are not accepted.")
    if not source.exists():
        if required:
            raise CarFolderReadError(f"{name}: required file missing.")
        return None
    if not source.is_file():
        raise CarFolderReadError(f"{name}: expected a regular file.")
    if source.stat().st_size > MAX_INPUT_BYTES:
        raise CarFolderReadError(f"{name}: file exceeds the 1 MiB limit.")
    with source.open("rb") as stream:
        blob = stream.read(MAX_INPUT_BYTES + 1)
    if len(blob) > MAX_INPUT_BYTES:
        raise CarFolderReadError(f"{name}: file exceeds the 1 MiB limit.")
    try:
        return blob.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CarFolderReadError(f"{name}: only UTF-8 text is supported.") from exc


def read_car_folder(folder: str | Path) -> dict[str, str]:
    """Return exact allowlisted file contents; never scan additional files."""
    directory = Path(folder).expanduser()
    if directory.is_symlink() or not directory.is_dir():
        raise CarFolderReadError("Select an existing, non-linked AC car data folder.")
    directory = directory.resolve(strict=True)
    result: dict[str, str] = {}
    for name in INPUT_NAMES:
        raw = _read_optional_file(directory, name, required=(name == "car.ini"))
        if raw is not None:
            result[name] = raw
    return result


def parse_ini_sections(text: str) -> dict[str, dict[str, str]]:
    """Preserve section identity; overlapping keys must not overwrite each other."""
    config = configparser.ConfigParser(
        interpolation=None,
        strict=True,
        inline_comment_prefixes=(";", "#"),
        empty_lines_in_values=False,
    )
    config.optionxform = str.upper
    try:
        config.read_string(text)
    except configparser.Error as exc:
        raise CarFolderReadError("INI format is invalid or has duplicate sections/keys.") from exc
    return {
        section.upper(): {
            key.upper(): value.strip()
            for key, value in config.items(section, raw=True)
        }
        for section in config.sections()
    }
