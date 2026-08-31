## 1. Extract testable logic into headers

- [ ] 1.1 Add `isValidGateCommand(const char* cmd)` to `arduino/valve_logic.h` and refactor `arduino/valves/valves.ino` to use it; verify `arduino-cli compile -b arduino:avr:uno arduino/valves` succeeds
- [ ] 1.2 Add `brightnessForPot(int adc)` to `arduino/measurement.h` and refactor `arduino/simple01/simple01.ino` to use it; verify `arduino-cli compile -b arduino:avr:uno arduino/simple01` succeeds
- [ ] 1.3 Confirm `arduino/sensors/sensors.ino` needs no new extraction (math already in `sensor_math.h`); verify `arduino-cli compile -b arduino:avr:uno arduino/sensors` succeeds

## 2. Expand AUnit unit tests

- [ ] 2.1 Add command-validation tests to `arduino-tests/test_valve_logic/` (`isValidGateCommand` valid/invalid cases); verify tests compile with EpoxyDuino make
- [ ] 2.2 Add brightness-mapping tests to `arduino-tests/test_measurement/` (`brightnessForPot` boundary cases); verify tests compile with EpoxyDuino make
- [ ] 2.3 Add mid-range golden-value cases to `arduino-tests/test_sensor_math/` if gaps found; verify tests compile with EpoxyDuino make
- [ ] 2.4 Run `make -C arduino-tests runtests` locally and verify all AUnit tests pass (0 failed)

## 3. Rename test projects to match sketches

- [ ] 3.1 Rename `test_valve_logic` → `test_valves`, `test_measurement` → `test_simple01`, `test_sensor_math` → `test_sensors`; update Makefiles, sketch filenames, and `APP_NAME` in each Makefile
- [ ] 3.2 Update Wokwi configs (`wokwi.toml`, `diagram.json`, `aunit.test.yaml`) in each renamed test folder; verify paths point to correct `.hex` output
- [ ] 3.3 Update `scripts/wokwi_test.sh`, `scripts/wokwi_test.ps1`, and `scripts/arduino_test.ps1` for renamed folders; verify `powershell -File scripts/arduino_test.ps1 -CompileOnly` succeeds

## 4. CI — unit tests (stage 1)

- [ ] 4.1 Rename `arduino-tests` job to `arduino-unit-tests` in `.github/workflows/ci.yml` (keep EpoxyDuino clone + `make -C arduino-tests runtests` steps unchanged); verify job name and steps are correct in the YAML

## 5. CI — integration tests (stage 2)

- [ ] 5.1 Remove `arduino-compile` job from `.github/workflows/ci.yml`
- [ ] 5.2 Rename `arduino-wokwi` to `arduino-integration-tests`; set `needs: arduino-unit-tests`; keep Wokwi CLI install, `wokwi_test.sh`, and artifact upload steps
- [ ] 5.3 Add optional production-sketch compile smoke inside integration job (`arduino/valves`, `simple01`, `sensors`); verify YAML compiles all three sketches before Wokwi run

## 6. Documentation and verification

- [ ] 6.1 Update `AGENTS.md` with sketch→test mapping table and three test tiers (unit: `make -C arduino-tests runtests`; integration: `wokwi_test.ps1`; optional hardware: `arduino_test.ps1 -Port COM8`)
- [ ] 6.2 Run `make -C arduino-tests runtests` and verify all unit tests pass
- [ ] 6.3 Run Wokwi suite locally if `WOKWI_CLI_TOKEN` is set (`powershell -File scripts/wokwi_test.ps1`) and verify integration tests pass
