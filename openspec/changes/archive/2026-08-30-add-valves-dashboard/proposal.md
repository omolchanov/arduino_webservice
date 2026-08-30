## Why

We need a dedicated dashboard to experiment with logical valves (AND/OR gates) on Arduino, separate from the existing Keypad, Sensors, and Digital Signal pages. The `arduino/valves.ino` sketch reads two button inputs, computes a gate output, and reports state over serial — but the Python app does not parse or display this data yet.

## What Changes

- Add serial parsing for valve status lines from `arduino/valves.ino` (`A = 0 | B = 1 | Y = 0 | Gate = AND`)
- Broadcast WebSocket events `{"type": "valve", "a": 0|1, "b": 0|1, "y": 0|1, "gate": "AND"|"OR"}` and expose valve fields in `GET /api/status`
- Add `POST /api/valve/gate` to send gate selection commands to Arduino (`A` for AND, `O` for OR)
- Add a new **Valves** dashboard at `GET /valves` (`static/valves.html`)
- Add gate dropdown (top-right), three live widgets (selected gate, inputs A/B, output Y), and a truth table for the selected gate
- Add **Valves** nav link to Keypad, Sensors, Digital Signal, and Valves pages
- Establish **one sketch per page**: this dashboard uses `arduino/valves.ino` only

## Capabilities

### New Capabilities

- `valves-display`: Valve serial ingestion from `valves.ino`, gate selection API, Valves dashboard, live widgets, and truth table

### Modified Capabilities

<!-- None — Keypad, Sensors, and Digital Signal specs are unchanged -->

## Impact

- **Arduino**: `arduino/valves.ino` is the dedicated firmware for the Valves dashboard; user uploads this sketch when using `/valves`
- **Backend**: `main.py` — valve parser, WebSocket broadcast, status API, `/valves` route, `POST /api/valve/gate` (first serial write in the project)
- **Frontend**: new `static/valves.html`; nav updates in `static/index.html`, `static/sensors.html`, and `static/digital.html`
- **Tests**: new `tests/test_valves.py` for parser, status API, gate command, and WebSocket cache

## Non-Goals

- Changing `arduino/valves.ino` serial format
- Additional gate types beyond AND/OR
- Server-side history storage or charts
- Combining valves firmware with keypad, sensors, or simple01 sketches
