from ..models.car import Car
from ..parsers.car_parser import clean_value, to_float


class DrivetrainParser:

    @staticmethod
    def apply(data: dict, car: Car) -> None:

        car.drivetrain = clean_value(data.get("type"))

        count = clean_value(data.get("count"))
        if count:
            try:
                car.gears = int(count)
            except ValueError:
                pass

        car.max_torque = to_float(data.get("max_torque"))

        # 🔥 REAL GEAR RATIOS (AC FORMAT)
        ratios = []

        for i in range(1, 10):  # max 9 Gänge
            key = f"gear_{i}"
            value = clean_value(data.get(key))

            if value:
                try:
                    ratios.append(float(value))
                except:
                    pass

        if ratios:
            car.gear_ratios = ratios

        # 🔥 FINAL DRIVE (AC uses FINAL)
        car.final_drive = to_float(data.get("final"))