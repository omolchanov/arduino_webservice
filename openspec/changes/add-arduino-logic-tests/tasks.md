## 1. Tooling setup

- [x] 1.0 Rename `tests/` → `pytest/` and update `AGENTS.md` / task docs to use `python -m pytest pytest/` (or `python -m unittest discover -s pytest`); verify all existing Python tests still pass
- [x] 1.1 Add `arduino-tests/arduino-cli.yaml` with Uno FQBN and `-I../arduino` include path; verify `arduino-cli compile` can resolve headers from a test sketch
- [x] 1.2 Add `scripts/arduino_test.ps1` skeleton (compile all sketches + test projects; optional `-Port COM8` for `arduino-cli test`); verify script runs without error when arduino-cli is installed

## 2. Valve logic

- [x] 2.1 Create `arduino/valve_logic.h` with `evalGate()` for AND/OR/NOT/NAND/NOR/XOR/XNOR; refactor `arduino/valves.ino` to use it; verify `arduino-cli compile -b arduino:avr:uno arduino/valves.ino` succeeds
- [x] 2.2 Add `arduino-tests/test_valve_logic/test_valve_logic.ino` with Unity truth-table tests for all 7 gates; verify `arduino-cli compile` on the test project succeeds
- [x] 2.3 Run `arduino-cli test -b arduino:avr:uno -p COM8 arduino-tests/` (Serial Monitor closed) and verify valve logic tests pass on the board

## 3. Sensor math

- [x] 3.1 Create `arduino/sensor_math.h` with `distanceCm`, `invertLight`, `tempC`; refactor `arduino/sensors/sensors.ino`; verify compile succeeds
- [x] 3.2 Add `arduino-tests/test_sensor_math/test_sensor_math.ino` with golden-value Unity tests; verify compile succeeds
- [x] 3.3 Run `arduino-cli test` on COM8 and verify sensor math tests pass

## 4. Measurement logic

- [x] 4.1 Create `arduino/measurement.h` with `adcToVolts`, `logicZone`, `currentMa`, `ledResistance`; refactor `arduino/simple01.ino`; verify compile succeeds
- [x] 4.2 Add `arduino-tests/test_measurement/test_measurement.ino` with boundary tests at 1.5 V and 3.0 V plus current/resistance cases; verify compile succeeds
- [x] 4.3 Run `arduino-cli test` on COM8 and verify measurement tests pass

## 5. Documentation and regression check

- [x] 5.1 Document Arduino test commands in `AGENTS.md` (install arduino-cli, compile, test on COM8, close Serial Monitor)
- [x] 5.2 Run existing Python tests (`python -m pytest pytest/`) and verify all pass unchanged
- [x] 5.3 Run `scripts/arduino_test.ps1 -Port COM8` end-to-end and verify all compile + test steps pass

## 6. CI (optional)

- [x] 6.1 Add GitHub Actions workflow to `arduino-cli compile` production sketches and all `arduino-tests/test_*` projects without a connected board; verify workflow passes on push
