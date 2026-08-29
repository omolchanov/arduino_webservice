## Why

`arduino/simple01.ino` now computes LED resistance (`ledVoltage / current`) and appends `| LED Resistance: X.X Ohm` to each `Pot:` serial line, but the Digital Signal dashboard has no resistance widgets and the backend `POT_PATTERN` regex no longer matches the extended line format — so potentiometer, detected-logic, and current widgets stop updating when the new firmware is flashed.

## What Changes

- Extend `Pot:` line parsing to accept the optional `| LED Resistance: <ohm> Ohm` suffix (backward-compatible with lines that omit resistance)
- Broadcast a new WebSocket event `{"type": "resistance", "ohm": <float>}` when a resistance value is present
- Add `last_led_resistance_ohm` to `GET /api/status` and WebSocket cache-on-connect
- Add two widgets on `/digital`:
  - **Resistance** — live reading with status dot, value formatted to 1 decimal, **Ω** unit label
  - **Resistance history** — rolling line chart with **Ω** Y-axis label, placed immediately after the mA history widget
- **BREAKING:** Deploying updated `main.py` without flashing the new `simple01.ino` (or vice versa) leaves pot/detected/current widgets broken on old vs new line formats respectively

## Capabilities

### New Capabilities

_None — all behavior extends the existing digital-display capability._

### Modified Capabilities

- `digital-display`: Extend potentiometer serial ingestion for the new line format with LED resistance; add resistance serial ingestion, status API field, WebSocket cache, live resistance widget, and resistance history graph.

## Impact

- **Arduino**: `arduino/simple01.ino` — no firmware changes (resistance measurement already implemented)
- **Backend**: `main.py` — extend parser, state, broadcasts, status API, WebSocket connect cache
- **Frontend**: `static/digital.html` — two new cards reusing existing card/chart/status-dot patterns; wire Clear button and localStorage history
- **Tests**: `tests/test_parse_simple01.py`, `tests/test_read_serial_simple01.py`, `tests/test_digital_api.py`
- **Specs**: `openspec/specs/digital-display/spec.md` — new requirements for resistance ingestion and widgets
