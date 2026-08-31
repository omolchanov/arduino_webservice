## 1. Wokwi project configs

- [x] 1.1 Add `wokwi.toml`, `diagram.json`, `aunit.test.yaml` to `arduino-tests/test_valve_logic`
- [x] 1.2 Add same files to `arduino-tests/test_sensor_math`
- [x] 1.3 Add same files to `arduino-tests/test_measurement`

## 2. Local runner

- [x] 2.1 Add `scripts/wokwi_test.ps1` (compile + wokwi-cli for all test projects)
- [x] 2.2 Verify script fails fast when `WOKWI_CLI_TOKEN` is unset

## 3. Documentation

- [x] 3.1 Document Wokwi CLI install, token setup, and run commands in `AGENTS.md`

## 4. Verification

- [x] 4.1 Run `scripts/wokwi_test.ps1` locally — all 3 projects pass
