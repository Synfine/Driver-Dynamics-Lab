from dataclasses import dataclass


@dataclass
class Car:
    manufacturer: str | None = None
    model: str | None = None
    mass: float | None = None
    steer_lock: float | None = None
    max_fuel: float | None = None
    drivetrain: str | None = None
    gears: int | None = None
    max_torque: float | None = None
    max_power: float | None = None
    limiter: int | None = None
    power_curve: str | None = None
    power_data: list[tuple[int, float]] | None = None
    gear_ratios: list[float] | None = None
    final_drive: float | None = None