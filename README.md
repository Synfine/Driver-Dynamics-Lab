# Driver Dynamics Lab

Driver Dynamics Lab is an early Python prototype for importing Assetto Corsa car
data, exporting normalized vehicle JSON, and running first-pass drivetrain and
acceleration analysis.

## Current Scope

- Read AC-style `car.ini`, `drivetrain.ini`, `engine.ini`, and `power.lut` files
- Parse core vehicle metadata, gear ratios, final drive, limiter, and power data
- Export normalized car data into `database/cars/<manufacturer>/<model>.json`
- Estimate shift points, wheel torque, and simple acceleration times
- Plot acceleration and wheel torque curves

## Project Layout

```text
database/
  cars/                  Exported vehicle JSON files
  schemas/               JSON schema definitions
docs/                    Architecture notes and roadmap
importer/
  sample_data/           Example AC input files
  src/                   Importer, parser, exporter, analyzer code
  tests/                 Test folder
visualization/           Plotting helpers
```

## Run

```powershell
python importer/src/main.py
```

The current script reads the files in `importer/sample_data/` and exports the
result into `database/cars/`.

## Next Development Steps

1. Turn the importer into a clean CLI that accepts an AC car folder path.
2. Add tests for INI parsing, LUT parsing, JSON export, and shift logic.
3. Separate raw AC values from derived physics values.
4. Add more Kunos car samples to validate the parser against real-world variety.
