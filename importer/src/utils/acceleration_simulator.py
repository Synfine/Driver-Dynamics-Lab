import math

class AccelerationSimulator:

    def simulate(self, car):
        print("\n--- ACCELERATION SIM START ---")

        if not self._validate(car):
            return [], {}

        state = self._init_state(car)
        results = []
        step = 0

        while True:
            step += 1

            # =========================
            # RPM + SHIFT
            # =========================
            rpm = self._calc_rpm(state, car)

            shifted = self._handle_shift(state, car, rpm)

            if shifted:
                rpm = state["rpm"]
            else:
                state["rpm"] = rpm

            # =========================
            # ENGINE
            # =========================
            torque = self._calc_engine_torque(car, rpm)
            wheel_force = self._calc_wheel_force(car, torque, state)

            # =========================
            # FORCES
            # =========================
            net_force = self._apply_resistance(state, wheel_force)
            accel = self._apply_grip_limit(car, state, net_force)

            # =========================
            # UPDATE
            # =========================
            self._update_state(state, accel)

            # =========================
            # SAVE
            # =========================
            results.append({
                "time": state["time"],
                "speed": state["velocity"] * 3.6,
                "rpm": state["rpm"],
                "gear": state["gear_index"] + 1
            })

            if step % 20 == 0:
                print(
                    f"[t={round(state['time'],2)}s] "
                    f"{round(state['velocity']*3.6,1)} km/h | "
                    f"{int(state['rpm'])} rpm | G{state['gear_index']+1}"
                )

            # STOP
            if state["velocity"] * 3.6 > 350:
                break

            if step > 3000:
                print("❌ LOOP BREAK")
                break

        print("--- ACCELERATION SIM END ---\n")
        return results, self._analyze(results)

    # =========================

    def _init_state(self, car):
        return {
            "time": 0.0,
            "velocity": 0.0,
            "gear_index": 0,
            "rpm": 1000.0,
            "dt": 0.05,

            "mass": car.mass or 1200,
            "final_drive": car.final_drive,
            "gear_ratios": car.gear_ratios,
            "wheel_radius": 0.3,
            "efficiency": 0.85,

            "last_shift_time": -1,
            "shift_delay": 0.3
        }

    # =========================

    def _calc_rpm(self, state, car):
        if state["velocity"] < 0.1:
            return 1000

        ratio = state["gear_ratios"][state["gear_index"]]

        rpm = (
            state["velocity"]
            / state["wheel_radius"]
            * ratio
            * state["final_drive"]
            * 60 / (2 * math.pi)
        )

        return max(rpm, 1000)

    # =========================

    def _handle_shift(self, state, car, rpm):
        max_rpm = car.power_data[-1][0]
        shift_rpm = max_rpm * 0.97

        if state["time"] - state["last_shift_time"] < state["shift_delay"]:
            return False

        if rpm >= shift_rpm and state["gear_index"] < len(state["gear_ratios"]) - 1:

            old_ratio = state["gear_ratios"][state["gear_index"]]
            state["gear_index"] += 1
            new_ratio = state["gear_ratios"][state["gear_index"]]

            rpm_after = rpm * (new_ratio / old_ratio)

            state["rpm"] = rpm_after
            state["last_shift_time"] = state["time"]

            print(f"🔄 SHIFT → G{state['gear_index']+1} | {int(rpm_after)} rpm")

            return True

        return False

    # =========================

    def _calc_engine_torque(self, car, rpm):
        data = car.power_data

        # unterhalb
        if rpm <= data[0][0]:
            return data[0][1]

        # oberhalb → sanfter Abfall statt Cut
        if rpm >= data[-1][0]:
            over = rpm - data[-1][0]
            base = data[-1][1]
            return max(base - over * 0.01, base * 0.6)

        # interpolation
        for i in range(len(data) - 1):
            r1, t1 = data[i]
            r2, t2 = data[i + 1]

            if r1 <= rpm <= r2:
                f = (rpm - r1) / (r2 - r1)
                return t1 + f * (t2 - t1)

        return data[-1][1]

    # =========================

    def _calc_wheel_force(self, car, torque, state):
        ratio = state["gear_ratios"][state["gear_index"]]

        wheel_torque = (
            torque
            * ratio
            * state["final_drive"]
            * state["efficiency"]
        )

        return wheel_torque / state["wheel_radius"]

    # =========================

    def _apply_resistance(self, state, force):
        v = state["velocity"]
        m = state["mass"]

        drag = 0.5 * 1.225 * 0.32 * 2.2 * v * v
        rolling = 0.015 * m * 9.81

        return max(force - drag - rolling, 0)

    # =========================

    def _apply_grip_limit(self, car, state, force):
        m = state["mass"]
        g = 9.81

        drive = getattr(car, "drivetrain", "RWD")

        grip = 1.1 * m * g * (1.0 if drive == "AWD" else 0.6)

        return min(force, grip) / m

    # =========================

    def _update_state(self, state, accel):
        dt = state["dt"]
        state["velocity"] += accel * dt
        state["time"] += dt

    # =========================

    def _validate(self, car):
        return (
            car.power_data
            and car.gear_ratios
            and car.final_drive
        )

    # =========================

    def _analyze(self, data):
        times = {"0-100": None, "100-200": None}

        for p in data:
            if p["speed"] >= 100 and times["0-100"] is None:
                times["0-100"] = p["time"]

            if p["speed"] >= 200 and times["100-200"] is None:
                times["100-200"] = p["time"]

        return times