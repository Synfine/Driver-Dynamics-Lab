class CarValidationError(Exception):
    pass


class CarValidator:
    @staticmethod
    def validate(car) -> None:
        errors = []

        # Pflichtfelder
        if not car.model:
            errors.append("Model is missing")

        if not car.manufacturer:
            errors.append("Manufacturer is missing")

        # Zahlen validieren
        if car.mass is None or car.mass <= 0:
            errors.append("Mass must be > 0")

        if car.steer_lock is None or car.steer_lock <= 0:
            errors.append("Steer lock must be > 0")

        if car.max_fuel is None or car.max_fuel <= 0:
            errors.append("Max fuel must be > 0")

        # Ergebnis
        if errors:
            raise CarValidationError("\n".join(errors))