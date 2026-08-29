## Why

We need a dedicated dashboard to experiment with digital logic levels (0 and 1) on Arduino, separate from the existing Sensors and Keypad pages. Each widget is backed by its own sketch; the first widget is a live graph of the logic signal driven by `arduino/simple01.ino`.

## What Changes

- Add serial parsing for `Logic 1 (HIGH) - LED ON` / `Logic 0 (LOW) - LED OFF` lines from `arduino/simple01.ino` (D8 drives an LED)
- Broadcast WebSocket events `{"type": "logic", "value": 0|1}` and expose `last_logic_value` in `GET /api/status`
- Add a new **Digital Signal** dashboard at `GET /digital` (`static/digital.html`)
- Add a **Logic signal** graph widget (Chart.js stepped line chart, rolling client-side history)
- Add **Digital Signal** nav link to Keypad, Sensors, and Digital pages
- Establish **one sketch per widget**: this widget uses `arduino/simple01.ino` only (no combined firmware)

## Capabilities

### New Capabilities

- `digital-display`: Digital logic signal ingestion from `simple01.ino`, Digital Signal dashboard, and live 0/1 graph widget

### Modified Capabilities

<!-- None — Sensors and Keypad specs are unchanged -->

## Impact

- **Arduino**: `arduino/simple01.ino` is the dedicated firmware for the logic graph widget (D8 drives LED ON/OFF, 1s toggle); user uploads this sketch when using `/digital`
- **Backend**: `main.py` — logic parser, WebSocket broadcast, status API, `/digital` route
- **Frontend**: new `static/digital.html`; nav updates in `static/index.html` and `static/sensors.html`
- **Dependencies**: Chart.js loaded from CDN on the Digital page only

## Non-Goals

- Combining multiple widgets into one Arduino sketch
- Merging with `sensors.ino` or keypad firmware
- Server-side history storage
- Multiple digital pins in phase 1 (D8 only via `simple01.ino`)
