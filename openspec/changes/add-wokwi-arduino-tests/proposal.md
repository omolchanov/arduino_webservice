## Why

EpoxyDuino runs AUnit on the host and CI only compiles sketches; neither executes real AVR firmware without a physical board on COM8. Wokwi emulation runs the compiled Uno binary in a simulator and checks AUnit serial output locally, closing the gap without hardware.

## What Changes

- Add `wokwi.toml`, `diagram.json`, and `aunit.test.yaml` to each `arduino-tests/test_*` project
- Add `scripts/wokwi_test.ps1` to compile all AUnit sketches and run them via Wokwi CLI
- Document Wokwi setup and local run commands in `AGENTS.md`
- Phase 2 (deferred): GitHub Actions `arduino-wokwi` CI job

## Capabilities

### New Capabilities

<!-- None — developer tooling only -->

### Modified Capabilities

<!-- None — no product-facing behavior changes -->

**Spec opt-out:** No product-facing behavior changes. This change sets `skip_specs: true` in `.openspec.yaml`.

## Impact

- **New files**: Wokwi configs per test project, `scripts/wokwi_test.ps1`
- **Tooling**: requires Wokwi CLI and `WOKWI_CLI_TOKEN` env var (internet for cloud simulation)
- **Tests**: same 3 AUnit projects; no sketch logic changes
- **CI**: unchanged in Phase 1

## Non-Goals

- Production sketch integration tests with virtual hardware (keypad, sensors)
- Replacing EpoxyDuino or COM8 hardware tests
- Committing Wokwi tokens to the repository
