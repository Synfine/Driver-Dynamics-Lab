"""DDL v0.2 independent regression tests. No dependency beyond Python stdlib."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from importer.src.inspect_car import main
from importer.src.readers.ac_folder_reader import (
    CarFolderReadError, parse_ini_sections, read_car_folder, MAX_INPUT_BYTES,
)
from importer.src.readers.car_folder_inspector import inspect_car_folder, parse_raw_lut


ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "importer" / "sample_data"
BASIC_CAR = (
    "[INFO]\nSCREEN_NAME=TOYOTA AE86 Tuned\n"
    "[BASIC]\nTOTALMASS=975\n"
    "[CONTROLS]\nSTEER_LOCK=450\n"
    "[FUEL]\nMAX_FUEL=50\n"
)
DRIVE = "[TRACTION]\nTYPE=RWD\n[GEARS]\nCOUNT=2\nGEAR_1=3.5\nGEAR_2=2.0\nFINAL=4.7\n"
ENGINE = "[HEADER]\nPOWER_CURVE=power.lut\n[ENGINE_DATA]\nLIMITER=8000\n"
LUT = "1000|50\n2000|80\n3000|90\n"


class TestSafeCarFolder(unittest.TestCase):
    def test_real_ae86_fixture_is_not_reinterpreted_as_calculated_power(self):
        result = inspect_car_folder(SAMPLE)
        self.assertEqual(result["manufacturer"], "TOYOTA")
        self.assertEqual(result["model"], "AE86 Tuned")
        self.assertEqual(result["mass"], 975.0)
        self.assertEqual(result["drivetrain"], "RWD")
        self.assertEqual(result["gears"], 5)
        self.assertEqual(result["limiter"], 8000)
        self.assertEqual(len(result["power_data"]), 7)
        self.assertEqual(result["max_power"], None)
        self.assertEqual(result["max_torque"], None)
        self.assertEqual(result["inspection_only"], True)

    def test_duplicate_key_names_in_distinct_sections_do_not_collide(self):
        parsed = parse_ini_sections("[BASIC]\nTYPE=ROAD\n[TRACTION]\nTYPE=RWD\n")
        self.assertEqual(parsed["BASIC"]["TYPE"], "ROAD")
        self.assertEqual(parsed["TRACTION"]["TYPE"], "RWD")

    def test_allows_comments_utf8_bom_and_inline_comments(self):
        parsed = parse_ini_sections("\ufeff[BASIC]\nTOTALMASS=975 ; in kg\n")
        self.assertEqual(parsed["BASIC"]["TOTALMASS"], "975")
        self.assertEqual(parse_raw_lut("1000|50 ; note\n2000|80\n"), [[1000, 50.0], [2000, 80.0]])

    def test_missing_car_file_is_rejected_even_when_others_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "engine.ini").write_text(ENGINE, encoding="utf-8")
            with self.assertRaises(CarFolderReadError):
                inspect_car_folder(tmp)

    def test_only_four_allowlisted_filenames_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_text(BASIC_CAR, encoding="utf-8")
            (root / "unrelated.txt").write_text("SECRET", encoding="utf-8")
            read = read_car_folder(root)
            self.assertEqual(list(read), ["car.ini"])
            self.assertNotIn("SECRET", str(read))

    def test_custom_lut_reference_is_rejected_even_if_other_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_text(BASIC_CAR, encoding="utf-8")
            (root / "engine.ini").write_text(
                "[HEADER]\nPOWER_CURVE=../../other.lut\n", encoding="utf-8"
            )
            (root / "power.lut").write_text(LUT, encoding="utf-8")
            with self.assertRaises(CarFolderReadError):
                inspect_car_folder(root)

    def test_incomplete_gear_count_is_rejected_not_silently_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_text(BASIC_CAR, encoding="utf-8")
            (root / "drivetrain.ini").write_text(
                "[TRACTION]\nTYPE=RWD\n[GEARS]\nCOUNT=2\nGEAR_1=3.5\n",
                encoding="utf-8",
            )
            with self.assertRaises(CarFolderReadError):
                inspect_car_folder(root)

    def test_oversize_file_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_bytes(b"x" * (MAX_INPUT_BYTES + 1))
            with self.assertRaises(CarFolderReadError):
                inspect_car_folder(root)

    def test_symlinked_physics_file_rejected_if_os_supports_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_text(BASIC_CAR, encoding="utf-8")
            other = root / "other.txt"
            other.write_text(ENGINE, encoding="utf-8")
            try:
                (root / "engine.ini").symlink_to(other)
            except (OSError, NotImplementedError):
                self.skipTest("Windows may require symlink privileges.")
            with self.assertRaises(CarFolderReadError):
                inspect_car_folder(root)

    def test_non_finite_and_non_monotone_lut_are_rejected(self):
        for text in ("1000|10\n900|20", "1000|NaN", "1000|inf", "1000|30\n1000|40"):
            with self.subTest(text=text), self.assertRaises(CarFolderReadError):
                parse_raw_lut(text)

    def test_no_implicit_car_selection_and_json_cli_has_no_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "car.ini").write_text(BASIC_CAR, encoding="utf-8")
            before = sorted(p.name for p in root.iterdir())
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["--car-dir", str(root), "--json"])
            self.assertEqual(exit_code, 0)
            parsed = json.loads(output.getvalue())
            self.assertEqual(parsed["mass"], 975.0)
            self.assertEqual(sorted(p.name for p in root.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
