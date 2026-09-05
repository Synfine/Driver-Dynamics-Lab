import matplotlib.pyplot as plt


def plot_acceleration(time, speed, rpm=None):
    fig, ax1 = plt.subplots()

    # =========================
    # SPEED
    # =========================
    ax1.plot(time, speed, label="Speed (km/h)")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Speed (km/h)")

    # =========================
    # RPM
    # =========================
    if rpm:
        ax2 = ax1.twinx()

        rpm_clean = [r if r is not None else 0 for r in rpm]

        ax2.plot(time, rpm_clean, linestyle="--", label="RPM")
        ax2.set_ylabel("RPM")

        # combined legend
        l1, lab1 = ax1.get_legend_handles_labels()
        l2, lab2 = ax2.get_legend_handles_labels()
        ax1.legend(l1 + l2, lab1 + lab2)
    else:
        ax1.legend()

    plt.title("Acceleration Simulation")
    plt.grid(True)
    plt.tight_layout()
    plt.show()