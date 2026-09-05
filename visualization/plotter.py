import matplotlib.pyplot as plt

from importer.src.utils.real_shift_analyzer import RealShiftAnalyzer


def plot_wheel_torque(car):
    rpm_range = range(1000, 8000, 100)

    all_curves = []

    # 🔥 Alle Gear-Kurven berechnen
    for i, ratio in enumerate(car.gear_ratios[:-1]):
        values = []

        for rpm in rpm_range:
            wt = RealShiftAnalyzer.get_wheel_torque(car, rpm, ratio)
            values.append(wt)

        all_curves.append(values)
        plt.plot(rpm_range, values, label=f"Gear {i+1}")

    # 🔥 SHIFT POINTS holen
    shift_points = RealShiftAnalyzer.analyze(car)

    # 🔥 VISUALISIERUNG DER SHIFT POINTS
    for gear_index, shift_rpm in shift_points:
        gear_idx = gear_index - 1

        if gear_idx < len(all_curves):
            curve = all_curves[gear_idx]

            # passenden Index im rpm_range finden
            try:
                idx = list(rpm_range).index(int(shift_rpm / 100) * 100)
            except ValueError:
                continue

            torque_value = curve[idx]

            # 🔴 Punkt zeichnen
            plt.scatter(shift_rpm, torque_value, s=80)

            # 🔴 vertikale Linie
            plt.axvline(x=shift_rpm, linestyle="--")

    plt.xlabel("RPM")
    plt.ylabel("Wheel Torque")
    plt.title("Wheel Torque per Gear (with Shift Points)")
    plt.legend()
    plt.grid()

    plt.show()