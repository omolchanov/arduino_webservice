## Why

`arduino/simple01.ino` now measures shunt current on A1 and prints `Current: X.X mA` on each `Pot:` line, but the Digital Signal dashboard has no widgets for current and the backend `POT_PATTERN` regex no longer matches the extended serial format — so potentiometer and detected-logic widgets stop updating when the new firmware is flashed.

## What Changes

- Extend `Pot:` line parsing to accept the optional `| Shunt: <v> V | Current: <mA> mA` suffix (backward-compatible with lines that omit current fields)
- Broadcast a new WebSocket event `{"type": "current", "ma": <float>}` when a current value is present
- Add `last_current_ma` to `GET /api/status` and WebSocket cache-on-connect
- Add two widgets on `/digital`:
  - **Current** — live mA reading with status dot (same UX as Potentiometer card)
  - **Current history** — rolling line chart (same UX as Potentiometer history card)
- **BREAKING:** Deploying updated `main.py` without flashing the new `simple01.ino` (or vice versa) leaves pot/detected widgets broken on old vs new line formats respectively

## Capabilities

### New Capabilities

_None — all behavior extends the existing digital-display capability._

### Modified Capabilities

- `digital-display`: Extend potentiometer serial ingestion for the new line format; add current serial ingestion, status API field, WebSocket cache, live current widget, and current history graph.

## Impact

- **Arduino**: `arduino/simple01.ino` — no firmware changes (current measurement already implemented)
- **Backend**: `main.py` — extend parser, state, broadcasts, status API, WebSocket connect cache
- **Frontend**: `static/digital.html` — two new cards reusing existing card/chart/status-dot patterns; wire Clear button and localStorage history
- **Tests**: `tests/test_parse_simple01.py`, `tests/test_read_serial_simple01.py`, `tests/test_digital_api.py`
- **Specs**: `openspec/specs/digital-display/spec.md` — new requirements for current ingestion and widgets
