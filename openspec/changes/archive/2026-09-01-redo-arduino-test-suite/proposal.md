## Why

The Arduino test suite has grown across three overlapping CI jobs (`arduino-tests`, `arduino-compile`, `arduino-wokwi`) without a clear unit-vs-integration split. Unit test coverage per production sketch is incomplete (inconsistent naming, logic still inline in `.ino` files), and the compile-only job adds no assertions while Wokwi re-compiles the same projects anyway.

## What Changes

- **Phase 1 — Unit tests:** One AUnit test project per production sketch (`valves`, `simple01`, `sensors`); extract remaining testable logic into shared headers; expand assertions; rename test folders for 1:1 sketch mapping
- **Phase 1 — CI:** Rename `arduino-tests` job to `arduino-unit-tests` (same EpoxyDuino + `make -C arduino-tests runtests` steps)
- **Phase 2 — CI:** Remove redundant `arduino-compile` job; rename `arduino-wokwi` to `arduino-integration-tests`; chain directly after unit tests
- **Phase 2 — Integration:** Keep Wokwi AUnit suite on simulated Uno via `scripts/wokwi_test.sh`; optionally retain production-sketch compile smoke inside integration job
- **Docs:** Update `AGENTS.md` with sketch→test mapping and three test tiers (unit / integration / optional COM8)

## Capabilities

### New Capabilities

<!-- None — developer tooling and test infrastructure only -->

### Modified Capabilities

<!-- None — no product-facing behavior changes -->

**Spec opt-out:** No product-facing behavior changes. This change sets `skip_specs: true` in `.openspec.yaml`.

## Impact

- **Headers:** `arduino/valve_logic.h`, `arduino/measurement.h` — new pure-logic helpers
- **Sketches:** `arduino/valves/valves.ino`, `arduino/simple01/simple01.ino` — use extracted helpers
- **Tests:** `arduino-tests/test_*` — rename, expand AUnit coverage
- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — two Arduino jobs instead of three
- **Scripts:** `scripts/wokwi_test.*`, `scripts/arduino_test.ps1` — path updates if test folders renamed
- **Docs:** `AGENTS.md`
- **Dependencies:** EpoxyDuino + AUnit (unit), arduino-cli + Wokwi CLI + `WOKWI_CLI_TOKEN` (integration)

## Non-Goals

- Production-sketch Wokwi scenarios with virtual wiring (keypad, sensors)
- Replacing AUnit or EpoxyDuino
- PlatformIO
- Testing `Serial.println` banners, debounce timing, or hardware I/O loops
- Changing Python API tests or dashboard behavior
