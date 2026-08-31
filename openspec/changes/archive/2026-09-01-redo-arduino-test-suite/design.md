## Context

See [proposal.md](proposal.md) for motivation.

Three production sketches (`arduino/valves/`, `arduino/simple01/`, `arduino/sensors/`) share pure-logic headers (`valve_logic.h`, `measurement.h`, `sensor_math.h`). Three AUnit test projects under `arduino-tests/test_*` exercise those headers. CI today runs four sequential jobs on `feature-*` pushes:

```
python-tests → arduino-tests → arduino-compile → arduino-wokwi
```

- `arduino-tests` already runs EpoxyDuino native unit tests (`make -C arduino-tests runtests`)
- `arduino-compile` only verifies AVR compilation (no assertions)
- `arduino-wokwi` compiles test projects again and runs them on Wokwi

Test project names do not match sketch names (`test_valve_logic` vs `valves`). Some sketch logic (gate command parsing, LED brightness mapping) remains inline and untested.

## Goals / Non-Goals

**Goals:**

- One AUnit test project per production sketch with 1:1 naming
- Complete unit test coverage for all extractable firmware logic
- Two-tier CI: unit (EpoxyDuino) then integration (Wokwi)
- Clear local commands: unit / integration / optional COM8

**Non-Goals:**

- Production-sketch Wokwi scenarios with virtual hardware
- Replacing AUnit, EpoxyDuino, or arduino-cli
- PlatformIO
- Testing serial banners, debounce timing, or pin I/O loops
- Changing Python tests or dashboard behavior

## Decisions

### 1. Test framework: AUnit (not arduino-cli alone)

**AUnit** provides assertions and `TestRunner` serial output. **arduino-cli** is the AVR compiler/uploader only — compile-only checks do not run tests.

| Runner | Role | When |
|--------|------|------|
| EpoxyDuino + make | Native unit tests | Local + CI stage 1 |
| arduino-cli + Wokwi CLI | AVR integration tests | CI stage 2 |
| arduino-cli + COM8 | Optional hardware | Local only |

**Alternative considered:** Unity — not in Arduino Library Manager; rejected.

### 2. One test project per sketch (rename)

| Sketch | Header | Current test | New name |
|--------|--------|--------------|----------|
| `valves` | `valve_logic.h` | `test_valve_logic` | `test_valves` |
| `simple01` | `measurement.h` | `test_measurement` | `test_simple01` |
| `sensors` | `sensor_math.h` | `test_sensor_math` | `test_sensors` |

Update Makefiles, Wokwi configs (`wokwi.toml`, `diagram.json`, `aunit.test.yaml`), and scripts (`wokwi_test.sh`, `wokwi_test.ps1`, `arduino_test.ps1`).

### 3. Extract remaining pure logic into headers

| Sketch | Function | Tests |
|--------|----------|-------|
| valves | `isValidGateCommand(const char* cmd) -> bool` | `"AND"`, `"xor"` valid; `"FOO"`, `""` invalid |
| simple01 | `brightnessForPot(int adc) -> int` | 614→0, 1023→255; below 614→0 |
| sensors | *(none)* | Extend golden values in existing tests |

Sketches call these helpers; pin reads, `Serial`, and timing stay in `.ino`.

### 4. CI pipeline (two Arduino jobs)

**Before:**
```
python-tests → arduino-tests → arduino-compile → arduino-wokwi
```

**After:**
```
python-tests → arduino-unit-tests → arduino-integration-tests
```

| Job | Steps |
|-----|-------|
| `arduino-unit-tests` | Clone EpoxyDuino + AUnit to parent dir; `make -C arduino-tests runtests` |
| `arduino-integration-tests` | arduino-cli + Wokwi CLI; `bash scripts/wokwi_test.sh`; upload reports |

Remove `arduino-compile`. Optionally add production-sketch compile smoke inside integration job:

```bash
arduino-cli compile -b arduino:avr:uno arduino/valves ...
arduino-cli compile -b arduino:avr:uno arduino/simple01 ...
arduino-cli compile -b arduino:avr:uno arduino/sensors ...
```

### 5. EpoxyDuino clone location (unchanged)

CI clones AUnit and EpoxyDuino into the **parent directory** (`cd ..` then clone). Per-test Makefiles use `include ../../../EpoxyDuino/EpoxyDuino.mk`.

### 6. Wokwi pass/fail (unchanged)

Each test project keeps `aunit.test.yaml`:

```yaml
steps:
  - wait-serial: "TestRunner summary:"
  - wait-serial: "0 failed"
```

Timeout: 45000 ms. `WOKWI_CLI_TOKEN` from GitHub secrets.

## Risks / Trade-offs

- **[Rename breaks local paths]** → Update all scripts and docs in same commit
- **[EpoxyDuino setup friction]** → CI clones automatically; document local clone-one-level-up in AGENTS.md
- **[Wokwi cloud dependency]** → Integration stage only; unit tests run offline
- **[Production compile smoke removed]** → Mitigate with optional compile step in integration job

## Migration Plan

1. Extract helpers into headers; refactor sketches
2. Expand AUnit tests; rename test folders
3. Update scripts and CI job names
4. Verify locally: `make -C arduino-tests runtests`
5. Push to `feature-redo-arduino-test-suite`; confirm CI passes both Arduino jobs

Rollback: git revert on feature branch.

## Open Questions

None — approach is settled.
