from pathlib import Path

from ..models.car import Car
from ..parsers.car_parser import clean_value, to_float
from ..readers.lut_reader import LutReader


class EngineParser:
    @staticmethod
    def apply(data: dict, car: Car) -> None:

        car.max_torque = to_float(data.get("max_torque"))
        car.max_power = to_float(data.get("max_power"))

        limiter = clean_value(data.get("limiter"))
        if limiter:
            try:
                car.limiter = int(limiter)
            except ValueError:
                pass

        car.power_curve = clean_value(data.get("power_curve"))

        if car.power_curve:
            lut_path = Path(__file__).resolve().parent.parent.parent / "sample_data" / car.power_curve
            car.power_data = LutReader.read(lut_path)