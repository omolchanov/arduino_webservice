## Why

`arduino/simple01.ino` was updated to emit a new multi-line serial format (`SIGNAL_PIN:` phase lines and `Pot:` reading lines). The Python backend still parses the old single-line `Generated: … | Potentiometer: … | Detected: …` format, so the Digital Signal dashboard receives no live data after uploading the new sketch.

## What Changes

- Replace the combined `parse_simple01_line()` regex with two parsers: `parse_signal_pin_line()` for `SIGNAL_PIN: Logic 0|1` lines and `parse_pot_line()` for `Pot: X.XX V | Logic: 0|UNDEFINED|1` lines
- Map pot `Logic: UNDEFINED` to detected state **`0.5`** (undefined zone) in WebSocket and status API
- Update **Detected logic LED** widget and history chart to use three states: `0`, `0.5`, `1`
- Add **grey markers** on the potentiometer history graph when detected state transitions to `0.5`
- Update unit tests for new line formats; old `Generated:` lines are no longer parsed
- **BREAKING**: Serial line format for `simple01.ino` ingestion changes; clients relying on the old combined line will stop receiving updates

## Capabilities

### New Capabilities

<!-- None -->

### Modified Capabilities

- `digital-display`: Serial ingestion from `simple01.ino`, detected three-state model (`0` / `0.5` / `1`), potentiometer graph undefined-zone markers

## Impact

- **Backend**: `main.py` — new parsers, `read_serial` dispatch, `last_detected_value` may be `0.5`
- **Frontend**: `static/digital.html` — detected widget/chart three-state display, grey pot-graph marker dataset
- **Tests**: `tests/test_parse_simple01.py`, `tests/test_read_serial_simple01.py`
- **Arduino**: `arduino/simple01.ino` already updated (no firmware changes in this change)
