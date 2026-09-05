from ..models.car import Car


def clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    return value.split(";")[0].strip()


def to_float(value: str | None) -> float | None:
    value = clean_value(value)
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


class CarParser:

    @staticmethod
    def parse_car(data: dict) -> Car:
        car = Car()

        # --- NAME ---
        name = clean_value(data.get("screen_name"))
        if name:
            parts = name.split()
            car.manufacturer = parts[0]
            car.model = " ".join(parts[1:])

        # --- WERTE ---
        car.mass = to_float(data.get("totalmass"))
        car.steer_lock = to_float(data.get("steer_lock"))
        car.max_fuel = to_float(data.get("max_fuel"))

        return car