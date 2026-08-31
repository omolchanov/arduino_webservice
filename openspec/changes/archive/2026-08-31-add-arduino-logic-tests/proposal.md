## Why

Python tests in `pytest/` validate serial line parsing and API behavior, but firmware logic (gate truth tables, sensor formulas, voltage thresholds) lives inline in Arduino sketches with no automated checks. Extracting pure logic into shared headers and adding Unity tests via `arduino-cli` catches firmware regressions before flashing, without duplicating formulas in Python.

## What Changes

- Extract pure logic from `arduino/valves.ino`, `arduino/simple01.ino`, and `arduino/sensors/sensors.ino` into shared headers under `arduino/` (`valve_logic.h`, `measurement.h`, `sensor_math.h`)
- Refactor sketches to call extracted helpers; behavior and serial output format stay the same
- Add a top-level `arduino-tests/` folder for Unity test projects (arduino-cli); rename existing `tests/` → `pytest/` for Python API tests
- Add `arduino-tests/arduino-cli.yaml` (or script flags) so test sketches include headers from `../arduino/`
- Add `scripts/arduino_test.ps1` to compile all sketches and run tests on COM8
- Document Arduino test commands in `AGENTS.md`
- Optional: GitHub Actions job to `arduino-cli compile` sketches and test projects (no board required)

## Capabilities

### New Capabilities

<!-- None — this is developer tooling and firmware refactor with unchanged serial/UI behavior -->

### Modified Capabilities

<!-- None — valves-display, sensors-display, and digital-display requirements are unchanged -->

**Spec opt-out:** No product-facing behavior changes. This change sets `skip_specs: true` in `.openspec.yaml`.

## Impact

- **Arduino firmware**: `arduino/valves.ino`, `arduino/simple01.ino`, `arduino/sensors/sensors.ino` refactored to use shared headers; serial formats unchanged
- **New files**: `arduino/*.h`, `arduino-tests/test_*/*.ino`, `arduino-tests/arduino-cli.yaml`, `scripts/arduino_test.ps1`
- **Tooling**: requires `arduino-cli`, AVR core, and Unity/ArduinoUnit library; on-device test run needs Arduino on COM8
- **Python**: rename `tests/` → `pytest/`; no logic changes to `main.py` or test cases
- **CI** (optional): compile-only smoke for firmware and test sketches

## Non-Goals

- Hardware-in-the-loop serial golden tests
- PlatformIO or host-side native test runner (v1 uses `arduino-cli` on real Uno)
- Testing `setup()` banners, debounce timing, or `Serial.println` strings
- Duplicating firmware formulas in Python tests
