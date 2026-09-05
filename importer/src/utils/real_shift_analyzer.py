class RealShiftAnalyzer:

    @staticmethod
    def get_interpolated_value(data, x):
        """
        Lineare Interpolation zwischen Punkten
        """
        for i in range(len(data) - 1):
            x1, y1 = data[i]
            x2, y2 = data[i + 1]

            if x1 <= x <= x2:
                ratio = (x - x1) / (x2 - x1)
                return y1 + ratio * (y2 - y1)

        return data[-1][1]

    @staticmethod
    def get_torque_at_rpm(car, rpm):
        """
        Berechnet Drehmoment aus Power Curve:
        Torque = (HP * 7127) / RPM
        """
        power = RealShiftAnalyzer.get_interpolated_value(car.power_data, rpm)

        if rpm == 0:
            return 0

        return (power * 7127) / rpm

    @staticmethod
    def get_wheel_torque(car, rpm, gear_ratio):
        torque = RealShiftAnalyzer.get_torque_at_rpm(car, rpm)
        return torque * gear_ratio * car.final_drive

    @staticmethod
    def analyze(car):
        if not car.power_data or not car.gear_ratios:
            return None

        results = []

        for i in range(len(car.gear_ratios) - 1):
            current_ratio = car.gear_ratios[i]
            next_ratio = car.gear_ratios[i + 1]

            shift_rpm = None

            min_rpm = 3000
            max_rpm = car.power_data[-1][0]

            for rpm in range(min_rpm, max_rpm, 100):  # 🔥 100 RPM steps

                # RPM nach Schalten
                new_rpm = rpm * (next_ratio / current_ratio)

                # Wheel Torque vergleichen
                wt_current = RealShiftAnalyzer.get_wheel_torque(
                    car, rpm, current_ratio
                )

                wt_next = RealShiftAnalyzer.get_wheel_torque(
                    car, new_rpm, next_ratio
                )

                # 👉 wenn nächster Gang mehr Beschleunigung hat → schalten
                SHIFT_TOLERANCE = 0.98
                RPM_STEP = 100
                if wt_next >= wt_current * SHIFT_TOLERANCE:
                    shift_rpm = rpm
                    break

            # fallback → wenn nichts gefunden → max RPM
            if shift_rpm is None:
                shift_rpm = car.power_data[-1][0]

            results.append((i + 1, int(shift_rpm)))

        return results