# DDL V0.2 — Safe AC car folder inspection (development branch)

**Branch:** `feature/ddl-v02-safe-car-folder-inspection`

This is the next conservative step after the AE86 sample-data importer. It is an
**opt-in, read-only inspection** of one explicitly selected Assetto Corsa
`content/cars/<vehicle>/data` folder. The existing sample-data parser,
physics analyzer, graph scripts, JSON exporter and GitHub main branch stay
unchanged. HOME's separate DDL V0.7.2 vehicle browser is also unchanged.

## Windows CMD usage

From the DDL repository root (after checking out this branch):

```bat
python -m importer.src.inspect_car --car-dir "C:\path\to\assettocorsa\content\cars\ks_toyota_ae86\data"
```

For normalized, **raw** JSON printed to the terminal:

```bat
python -m importer.src.inspect_car --car-dir "C:\path\to\assettocorsa\content\cars\ks_toyota_ae86\data" --json
```

No path is assumed and no interactive folder scan is performed. The full
`--car-dir` must be supplied explicitly. The user can preview any valid,
supported car data folder without altering the installation or DDL database.
`--json` writes to stdout only; it does **not** update
`database/cars` or generate plots.

The first check can be run against the checked-in sample:

```bat
python -m importer.src.inspect_car --car-dir "importer\sample_data"
```

## Strict current limits

- Only `car.ini` is mandatory. Optional: `drivetrain.ini`,
  `engine.ini`, `power.lut`. No `data.acd` unpacking yet.
- Each file max 1 MiB; file contents are UTF-8 only, including BOM.
  Legacy codepages are deliberately rejected until a safe encoding strategy
  is reviewed.
- Directory must exist and not itself be a symlink; symlinked physics
  files are rejected. No arbitrary INI-supplied LUT paths are read.
- `engine.ini [HEADER] POWER_CURVE` must name `power.lut` if present.
  A different LUT filename is flagged rather than substituted or fetched.
- INI keys are scoped to their own sections. Duplicate keys and invalid
  basic numeric fields are errors, not guessed away.
- Specified gear count must have that many positive gear ratios.
- Raw `power.lut` values remain **unconverted ordinates**; do not call
  them measured horsepower or claim accurate torque/acceleration.
  `max_power`/`max_torque` remain `null`.
- Steering angle, AC vehicle mass and fuel are reported **as stored by
  the source**. No driver-mass corrections, tire grip estimation or
  real-world spec equivalence is inferred.
- No network code, HOME endpoints, watchers, arbitrary file writes, or
  automatic import into the user's database.

## Regression tests

From the DDL repository root:

```bat
python -m unittest discover -s importer/tests -p "test_*.py" -v
```

New tests cover a real AE86 sample, section-key isolation, BOM/comments,
missing mandatory files, nonallowlisted files, unexpected LUT paths,
incomplete gear count, oversize files, symlinks, invalid LUT ordering,
and a read-only JSON stdout run.

**Not yet accepted:** The full test command has not been run on the owner's
Windows Python 3.13 installation in this branch; no new car has been imported
from the actual AC installation. Verify those before merging.

## Next guarded steps

1. Owner runs the tests and a **real car folder inspection** from a selected
   local AC vehicle. Prefer a stock Kunos vehicle first, then a mod.
2. Compare reported values against the original INI sections and in-game
   data. Do not infer units or performance not verified in source.
3. Once data provenance and formats pass, connect a **manual** DDL JSON
   export (with review and explicit destination) to HOME's current read-only
   vehicle browser. This should happen in a separate branch and requires
   user approval for the first write.
4. Only later: physically derived wheel torque, shift-point and speed
   curves, clearly labeled with assumptions and error bounds.
