## Context

Firmware sketches under `arduino/` embed business logic directly in `loop()` — gate evaluation in `valves.ino`, ADC/voltage/threshold math in `simple01.ino`, and sensor formulas in `sensors/sensors.ino`. Python tests in `pytest/` validate serial parsing and API behavior only; they do not exercise firmware calculations.

See [proposal.md](proposal.md) for motivation. Serial formats and dashboard behavior remain unchanged.

```
arduino/                       → production sketches + shared *.h
arduino-tests/test_*/          → AUnit tests (arduino-cli)
pytest/                        → Python API tests (pytest / unittest)
```

## Goals / Non-Goals

**Goals:**

- Single source of truth for pure firmware logic in `arduino/*.h` headers
- Unity unit tests in `arduino-tests/`; Python tests in `pytest/` (separate folders)
- `arduino-cli test` on real Uno (COM8) for logic assertions locally
- `arduino-cli compile` smoke for all sketches and test projects (CI-friendly)
- `scripts/arduino_test.ps1` and `AGENTS.md` documentation

**Non-Goals:**

- PlatformIO or host-side native test runner (v1)
- Hardware-in-the-loop serial golden tests
- Testing debounce timing, `setup()` banners, or `Serial.println` strings
- Duplicating formulas in Python
- Changing `main.py`, dashboards, or existing Python tests

## Decisions

### 1. Folder layout

| Path | Purpose |
|------|---------|
| `arduino/*.h` | Shared pure-logic headers |
| `arduino/*.ino` | Production sketches (thin loops) |
| `arduino-tests/test_*/` | Unity test projects (arduino-cli) |
| `pytest/` | Python API tests (pytest / unittest) |

**Alternative considered:** `arduino/test/` — rejected; Arduino tests live in top-level `arduino-tests/`, not inside `arduino/`.

**Alternative considered:** keep `tests/` for Python — rejected; renamed to `pytest/` for clear symmetry with `arduino-tests/`.

### 2. Shared headers and extracted functions

| Header | Sketch | Functions |
|--------|--------|-----------|
| `arduino/valve_logic.h` | `valves.ino` | `evalGate(const char* gate, bool a, bool b) -> bool` for AND, OR, NOT, NAND, NOR, XOR, XNOR |
| `arduino/sensor_math.h` | `sensors/sensors.ino` | `distanceCm(long duration)`, `invertLight(int adc)`, `tempC(int lm35Adc)` |
| `arduino/measurement.h` | `simple01.ino` | `adcToVolts(int adc)`, `logicZone(float voltage)` → 0 / 0.5 / 1, `currentMa(int shuntAdc, float shuntOhms)`, `ledResistance(float ledV, float currentA)` |

Sketches keep pin reads, `digitalWrite`, and serial formatting inline; only pure math/logic moves to headers.

Constants (`SHUNT_RESISTOR`, threshold 1.5 V / 3.0 V) live in headers as `#define` or `constexpr` so tests and sketches share them.

### 3. Test framework: AUnit via arduino-cli compile/upload

Use **AUnit** (`arduino-cli lib install "AUnit"`). Unity is not in the Library Manager; arduino-cli v1.5 has no `test` subcommand.

```bash
powershell -File scripts/arduino_test.ps1 -CompileOnly
powershell -File scripts/arduino_test.ps1 -Port COM8
```

Sketches live in `arduino/valves/`, `arduino/simple01/`, and `arduino/sensors/`; shared headers in `arduino/*.h`. Hardware tests upload each AUnit sketch and read pass/fail from serial via `scripts/read_aunit_serial.py`.

**Alternative considered:** PlatformIO native — rejected (user chose arduino-cli only).

**Alternative considered:** host-arduino-core for CI logic runs — deferred to optional v2.

### 4. Include path for test sketches

Add `arduino-tests/arduino-cli.yaml` with build properties so test sketches can `#include "valve_logic.h"` from `../arduino/`:

```yaml
board_options:
  board: arduino:avr:uno
build_properties:
  compiler.cpp.extra_flags: "-I../arduino"
```

The PowerShell script passes equivalent flags via `--build-property compiler.cpp.extra_flags=-I../arduino`.

### 5. Test coverage per domain

**`test_valve_logic`** — truth tables for all 7 gates:

| Gate | Key cases |
|------|-----------|
| AND | (0,0)→0, (0,1)→0, (1,1)→1 |
| OR | (0,0)→0, (1,0)→1, (1,1)→1 |
| NOT | A=0→1, A=1→0 (B ignored) |
| NAND/NOR/XOR/XNOR | full 4-row truth table each |

**`test_sensor_math`** — golden values:

- `distanceCm(580)` ≈ 10.0 cm (duration × 0.0343 / 2)
- `invertLight(0)` → 1023, `invertLight(1023)` → 0
- `tempC(205)` ≈ 25.0 °C (LM35 formula)

**`test_measurement`** — boundary tests:

- `logicZone(1.49)` → 0, `logicZone(1.50)` → 0.5, `logicZone(2.99)` → 0.5, `logicZone(3.00)` → 1
- `adcToVolts(0)` → 0.0, `adcToVolts(1023)` → 5.0
- `currentMa` and `ledResistance` with known ADC inputs

### 6. Run script (`scripts/arduino_test.ps1`)

Script responsibilities:

1. Verify `arduino-cli` is on PATH
2. `arduino-cli compile` for `valves.ino`, `simple01.ino`, `sensors/sensors.ino`
3. `arduino-cli compile` for each `arduino-tests/test_*` project
4. If `-Port COM8` (default): run `arduino-cli test` on `arduino-tests/`
5. Exit non-zero on compile or test failure

Close Serial Monitor before test run (same rule as uvicorn).

### 7. CI (optional)

GitHub Actions job: install arduino-cli + AVR core, run compile steps only (no board). Full logic tests remain a local developer step with hardware.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  valve_logic.h  │◄────│  valves.ino      │
└────────┬────────┘     └──────────────────┘
         │
         ▼
┌─────────────────┐
│ test_valve_logic│  arduino-cli test (COM8)
└─────────────────┘

pytest/  ──serial contract──►  main.py  (unchanged)
```

## Risks / Trade-offs

- **[Tests need physical board]** → CI compiles only; document local `arduino-cli test` in AGENTS.md
- **[Refactor may drift serial output]** → No Python test changes expected; manual smoke flash after refactor
- **[Float comparisons on AVR]** → Use `TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)` in Unity
- **[COM8 shared with uvicorn]** → Script docs: stop uvicorn / close Serial Monitor before tests

## Migration Plan

1. Extract headers and refactor one sketch at a time (valves → sensors → simple01)
2. Add matching test project after each extraction
3. Flash sketch and confirm dashboard still works (manual)
4. No rollback needed beyond git revert; serial format unchanged

## Open Questions

None — approach is settled (arduino-cli + Unity on Uno, separate `arduino-tests/` folder, skip_specs).
