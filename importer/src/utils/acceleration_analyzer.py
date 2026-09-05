import matplotlib.pyplot as plt


def plot_acceleration(time, speed, rpm=None):
    """
    Plottet Acceleration Daten sauber:
    - Speed vs Time (Hauptachse)
    - RPM optional (zweite Achse)
    """

    # --- VALIDATION ---
    if not time or not speed:
        print("❌ No data for plotting")
        return

    if len(time) != len(speed):
        print("❌ Time/Speed length mismatch")
        return

    # --- FIGURE ---
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # --- SPEED ---
    ax1.plot(time, speed, linewidth=2, label="Speed (km/h)")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Speed (km/h)")
    ax1.grid(True, alpha=0.3)

    # --- RPM (OPTIONAL) ---
    if rpm is not None and len(rpm) == len(time):
        # None Werte rausfiltern
        rpm_clean = [r if r is not None else 0 for r in rpm]

        ax2 = ax1.twinx()
        ax2.plot(time, rpm_clean, linestyle="--", linewidth=1.5, label="RPM")
        ax2.set_ylabel("RPM")

        # --- COMBINED LEGEND ---
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2)

    else:
        ax1.legend()

    # --- TITLE ---
    plt.title("Acceleration Simulation")

    # --- LAYOUT ---
    plt.tight_layout()

    # --- SHOW ---
    plt.show()