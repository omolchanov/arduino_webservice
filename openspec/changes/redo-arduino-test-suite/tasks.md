## 1. Extract testable logic into headers

- [x] 1.1 Add `isValidGateCommand(const char* cmd)` to `arduino/valve_logic.h` and refactor `arduino/valves/valves.ino` to use it; verify `arduino-cli compile -b arduino:avr:uno arduino/valves` succeeds
- [x] 1.2 Add `brightnessForPot(int adc)` to `arduino/measurement.h` and refactor `arduino/simple01/simple01.ino` to use it; verify `arduino-cli compile -b arduino:avr:uno arduino/simple01` succeeds
- [x] 1.3 Confirm `arduino/sensors/sensors.ino` needs no new extraction (math already in `sensor_math.h`); verify `arduino-cli compile -b arduino:avr:uno arduino/sensors` succeeds

## 2. Expand AUnit unit tests

- [x] 2.1 Add command-validation tests to `arduino-tests/test_valves/` (`isValidGateCommand` valid/invalid cases); verify tests compile with EpoxyDuino make
- [x] 2.2 Add brightness-mapping tests to `arduino-tests/test_simple01/` (`brightnessForPot` boundary cases); verify tests compile with EpoxyDuino make
- [x] 2.3 Add mid-range golden-value cases to `arduino-tests/test_sensors/`; verify tests compile with EpoxyDuino make
- [x] 2.4 Run `make -C arduino-tests runtests` locally and verify all AUnit tests pass (0 failed)

## 3. Rename test projects to match sketches

- [x] 3.1 Rename `test_valve_logic` → `test_valves`, `test_measurement` → `test_simple01`, `test_sensor_math` → `test_sensors`; update Makefiles, sketch filenames, and `APP_NAME` in each Makefile
- [x] 3.2 Valves integration uses co-located `arduino/valves/diagram.json`, `wokwi.toml`, and `valves.integration.yaml`
- [x] 3.3 Update `scripts/wokwi_integration_test.sh`, `scripts/wokwi_integration_test.ps1`, and `scripts/arduino_test.ps1` for renamed folders

## 4. CI — unit tests (stage 1)

- [x] 4.1 Rename `arduino-tests` job to `arduino-unit-tests` in `.github/workflows/ci.yml`

## 5. CI — integration tests (stage 2)

- [x] 5.1 Remove `arduino-compile` job from `.github/workflows/ci.yml`
- [x] 5.2 Add `arduino-integration-tests` job with Wokwi valves integration; `needs: arduino-unit-tests`
- [ ] 5.3 Add optional production-sketch compile smoke inside integration job (`arduino/valves`, `simple01`, `sensors`)

## 6. Documentation and verification

- [x] 6.1 Update `AGENTS.md` with sketch→test mapping and test tiers
- [x] 6.2 Run `make -C arduino-tests runtests` and verify all unit tests pass (CI)
- [x] 6.3 Run Wokwi valves integration on GitHub Actions with `WOKWI_CLI_TOKEN`
