import matplotlib.pyplot as plt

from importer.src.utils.real_shift_analyzer import RealShiftAnalyzer


def rpm_to_speed_kmh(rpm, gear_ratio, final_drive, wheel_radius=0.3):
    wheel_rpm = rpm / (gear_ratio * final_drive)
    wheel_circumference = 2 * 3.141592653589793 * wheel_radius
    speed_m_per_min = wheel_rpm * wheel_circumference
    return speed_m_per_min * 60 / 1000


def plot_wheel_torque(car):
    rpm_range = range(1000, car.power_data[-1][0] + 100, 100)

    all_curves = []

    # 🔥 Alle Gear-Kurven berechnen
    for i, ratio in enumerate(car.gear_ratios):
        speeds = []
        wheel_torques = []

        for rpm in rpm_range:
            speed = rpm_to_speed_kmh(rpm, ratio, car.final_drive)
            wheel_torque = RealShiftAnalyzer.get_wheel_torque(car, rpm, ratio)

            speeds.append(speed)
            wheel_torques.append(wheel_torque)

        all_curves.append((speeds, wheel_torques))
        plt.plot(speeds, wheel_torques, label=f"Gear {i+1}")

    # 🔥 SHIFT POINTS holen
    shift_points = RealShiftAnalyzer.analyze(car)

    # 🔥 VISUALISIERUNG DER SHIFT POINTS
    for gear_index, shift_rpm in shift_points:
        gear_idx = gear_index - 1

        if gear_idx < len(all_curves):
            ratio = car.gear_ratios[gear_idx]
            shift_speed = rpm_to_speed_kmh(shift_rpm, ratio, car.final_drive)
            torque_value = RealShiftAnalyzer.get_wheel_torque(car, shift_rpm, ratio)

            # 🔴 Punkt zeichnen
            plt.scatter(shift_speed, torque_value, s=80)

            # 🔴 vertikale Linie
            plt.axvline(x=shift_speed, linestyle="--")

    plt.xlabel("Speed (km/h)")
    plt.ylabel("Wheel Torque (Nm)")
    plt.title("Wheel Torque by Speed (with Shift Points)")
    plt.legend()
    plt.grid()

    plt.show()
