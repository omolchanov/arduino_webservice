## Context

Three AUnit test projects under `arduino-tests/test_*` validate shared headers in `arduino/*.h`. EpoxyDuino runs them natively on the host; `arduino_test.ps1 -Port COM8` runs them on real hardware. Wokwi adds AVR-realistic execution without a board.

## Goals / Non-Goals

**Goals:**

- Run `test_valve_logic`, `test_sensor_math`, and `test_measurement` on simulated Arduino Uno via Wokwi CLI
- Single local entry point: `scripts/wokwi_test.ps1`
- Pass/fail via AUnit serial summary (same as `read_aunit_serial.py`)

**Non-Goals:**

- CI integration in Phase 1
- Virtual wiring for production sketches
- Wokwi VS Code extension as a requirement

## Decisions

### 1. Co-located Wokwi config

Each `arduino-tests/test_*/` folder gets:

| File | Purpose |
|------|---------|
| `wokwi.toml` | Points to arduino-cli build output `.hex` / `.elf` |
| `diagram.json` | Minimal Arduino Uno (no extra parts) |
| `aunit.test.yaml` | Waits for AUnit `TestRunner summary` and `0 failed` |

### 2. Build output paths

`arduino-cli compile` with `--output-dir build` produces `build/<sketch>.ino.hex` and `.elf` at the project root (no `arduino.avr.uno` subfolder when using `--output-dir`).

### 3. Pass/fail detection

Automation scenario:

```yaml
steps:
  - command: wait-serial
    expect: "TestRunner summary:"
  - command: wait-serial
    expect: "0 failed"
```

Timeout: 45000 ms (sketches use 2s boot delay + `while (!Serial)`).

### 4. Local runner (`scripts/wokwi_test.ps1`)

1. Require `arduino-cli`, `wokwi-cli`, and `$env:WOKWI_CLI_TOKEN`
2. For each `arduino-tests/test_*`: compile with `-I../../arduino`, run `wokwi-cli . --scenario aunit.test.yaml --timeout 45000`
3. Exit non-zero on missing token, compile failure, or Wokwi failure

### 5. Token handling

`WOKWI_CLI_TOKEN` is set in the developer environment only. Never committed.

## Risks

- **Cloud simulation**: firmware uploaded to Wokwi servers during test runs
- **Internet required**: unlike EpoxyDuino or COM8
- **Monthly limits**: free tier ~50 min simulation time
