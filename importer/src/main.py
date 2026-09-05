import sys
from pathlib import Path

# =========================
# PROJECT ROOT SETUP
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMPORTER_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# =========================
# IMPORTS
# =========================

# MODELS
from importer.src.models.car import Car

# PARSERS
from importer.src.parsers.car_parser import CarParser
from importer.src.parsers.drivetrain_parser import DrivetrainParser
from importer.src.parsers.engine_parser import EngineParser

# READERS
from importer.src.readers.ini_reader import IniReader

# EXPORT
from importer.src.exporters.json_exporter import JsonExporter

# UTILS
from importer.src.utils.slug import slugify

# VALIDATION
from importer.src.validators.car_validator import CarValidator

# ANALYSIS
from importer.src.utils.power_analyzer import PowerAnalyzer
from importer.src.utils.real_shift_analyzer import RealShiftAnalyzer

# PHYSICS
from importer.src.utils.acceleration_simulator import AccelerationSimulator

# VISUALIZATION
from visualization.plot_acceleration import plot_acceleration
from visualization.plotter import plot_wheel_torque


# =========================
# PARSING
# =========================
def parse_files(file_paths):
    car = Car()

    for file_path in file_paths:
        print(f"\n📄 Processing: {file_path.name}")
        data = IniReader.read(file_path)

        if file_path.name == "car.ini":
            base_car = CarParser.parse_car(data)

            car.manufacturer = base_car.manufacturer
            car.model = base_car.model
            car.mass = base_car.mass
            car.steer_lock = base_car.steer_lock
            car.max_fuel = base_car.max_fuel

        elif file_path.name == "drivetrain.ini":
            DrivetrainParser.apply(data, car)

        elif file_path.name == "engine.ini":
            EngineParser.apply(data, car)

    return car


# =========================
# VALIDATION
# =========================
def validate_car(car):
    try:
        CarValidator.validate(car)
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


# =========================
# ANALYSIS
# =========================
def run_analysis(car):

    # 🔍 DEBUG POWER DATA
    print("\n🔍 DEBUG POWER DATA:")

    if not car.power_data:
        print("❌ NO POWER DATA")
    else:
        for p in car.power_data[:10]:
            print(p)

        print("Max torque:", max([p[1] for p in car.power_data]))

    # TORQUE PLOT
    try:
        plot_wheel_torque(car)
    except Exception as e:
        print(f"⚠️ Torque plot failed: {e}")

    # POWER ANALYSIS
    if car.power_data:
        try:
            analysis = PowerAnalyzer.analyze(car.power_data)

            if analysis:
                print("\n📊 POWER ANALYSIS:")
                print(f"Peak Power: {analysis['peak_power']} HP")
                print(f"Peak RPM:   {analysis['peak_rpm']}")
        except Exception as e:
            print(f"⚠️ Power analysis failed: {e}")

    # SHIFT ANALYSIS
    try:
        shifts = RealShiftAnalyzer.analyze(car)

        if shifts:
            print("\n🏁 REAL SHIFT POINTS:")
            for gear, rpm in shifts:
                print(f"Gear {gear} → shift at {rpm} RPM")
    except Exception as e:
        print(f"⚠️ Shift analysis failed: {e}")


# =========================
# EXPORT
# =========================
def export_car(car, project_root):
    try:
        manufacturer_slug = slugify(car.manufacturer or "unknown")
        model_slug = slugify(car.model or "unknown")

        output = project_root / "database" / "cars" / manufacturer_slug / f"{model_slug}.json"

        output.parent.mkdir(parents=True, exist_ok=True)
        JsonExporter.export(car, output)

        print(f"\n✅ Exported → {output}")

    except Exception as e:
        print(f"⚠️ Export failed: {e}")


# =========================
# SIMULATION
# =========================
def run_simulation(car):
    print("\n🚀 START ACCELERATION SIMULATION")

    simulator = AccelerationSimulator()
    accel_data, times = simulator.simulate(car)

    if not accel_data:
        print("❌ No acceleration data")
        return None, None

    return accel_data, times


# =========================
# VISUALIZATION
# =========================
def visualize_results(accel_data, times):

    if not accel_data:
        print("❌ No data to visualize")
        return

    time = [d["time"] for d in accel_data]
    speed = [d["speed"] for d in accel_data]
    rpm = [d["rpm"] for d in accel_data]

    max_speed = max(speed)
    print(f"\n🏁 Top Speed: {max_speed:.1f} km/h")

    print("\n⏱ ACCELERATION TIMES:")

    print(
        f"0-100 km/h: {times['0-100']:.2f} s"
        if times.get("0-100")
        else "0-100 km/h: not reached"
    )

    print(
        f"100-200 km/h: {times['100-200']:.2f} s"
        if times.get("100-200")
        else "100-200 km/h: not reached"
    )

    try:
        plot_acceleration(time, speed, rpm)
    except Exception as e:
        print(f"⚠️ Plot failed: {e}")


# =========================
# CORE PIPELINE
# =========================
def process_all_files(file_paths, project_root):

    car = parse_files(file_paths)

    print("\n🚗 FINAL CAR:")
    print(car)

    if not validate_car(car):
        return

    run_analysis(car)
    export_car(car, project_root)

    accel_data, times = run_simulation(car)

    if not accel_data:
        return

    visualize_results(accel_data, times)


# =========================
# ENTRYPOINT
# =========================
def main():
    project_root = PROJECT_ROOT
    data_dir = IMPORTER_ROOT / "sample_data"

    ini_files = list(data_dir.glob("*.ini"))

    print(f"Found {len(ini_files)} files...\n")

    if not ini_files:
        print("❌ No .ini files found")
        return

    process_all_files(ini_files, project_root)


if __name__ == "__main__":
    main()
