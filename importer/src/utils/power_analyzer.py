class PowerAnalyzer:

    @staticmethod
    def analyze(power_data):
        if not power_data:
            return None

        max_power = 0
        max_rpm = 0

        for rpm, power in power_data:
            if power > max_power:
                max_power = power
                max_rpm = rpm

        return {
            "peak_power": max_power,
            "peak_rpm": max_rpm
        }