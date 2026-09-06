## Why

The project already has a software 2-to-1 multiplexer sketch (`arduino/mux/mux.ino`) that reports `A`, `DI0`, `DI1`, and `DO` over serial, but the FastAPI app does not expose this data on the web. A dedicated **Combination Devices** page will let users see the MUX truth table and live D13 output on hardware, matching the learning flow used for the Valves dashboard.

## What Changes

- Add serial parsing for MUX status lines from `arduino/mux/mux.ino` (`A=0  DI0=1  DI1=0  ->  DO=1  (selected: DI0)`)
- Broadcast WebSocket events `{"type": "mux", "a": 0|1, "di0": 0|1, "di1": 0|1, "do": 0|1}` and expose MUX fields in `GET /api/status`
- Add a new **Combination Devices** dashboard at `GET /combination` (`static/combination.html`)
- Add live widgets for address **A**, inputs **DI0** / **DI1**, and output **DO** (D13), plus an 8-row MUX truth table with the active row highlighted (same pattern as Valves)
- Add **Combination Devices** nav link to all existing dashboard pages
- Establish **one sketch per page**: this dashboard uses `arduino/mux/mux.ino` only (read-only; no serial commands from the web)

## Capabilities

### New Capabilities

- `combination-devices-display`: MUX serial ingestion from `mux.ino`, Combination Devices dashboard, live widgets, and truth-table row highlighting

### Modified Capabilities

<!-- None — Keypad, Sensors, Digital Signal, Valves, and Display specs are unchanged -->

## Impact

- **Arduino**: `arduino/mux/mux.ino` is the dedicated firmware for the Combination Devices dashboard; user uploads this sketch when using `/combination`
- **Backend**: `main.py` — MUX parser, WebSocket broadcast, status API fields, `/combination` route
- **Frontend**: new `static/combination.html`; nav updates in all `static/*.html` dashboards
- **Tests**: new `pytest/test_combination.py` for parser, status API, page load, and WebSocket cache

## Non-Goals

- Changing `arduino/mux/mux.ino` serial format
- Web controls to drive D2/D3/D4 from the browser (hardware jumpers only)
- Server-side history storage or charts
- Combining MUX firmware with keypad, sensors, valves, or other sketches
