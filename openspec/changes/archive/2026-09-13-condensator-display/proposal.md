## Why

The `arduino/condensator/condensator.ino` sketch measures capacitor voltage and charge (Q) during charge/discharge cycles over serial, but the web UI has no page to visualize this data. A dedicated **Condensator** dashboard with live values and time-series graphs (including RC asymptotes) will make the capacitor behavior visible during lab work.

## What Changes

- Extend `main.py` serial parser for condensator lines (`Charging...`, `Discharging...`, `V = … V   Q = … uC`) and broadcast via WebSocket
- Add **Condensator** page at `GET /condensator` with two widgets: **Voltage** (V) and **Charge Q** (µC)
- Each widget shows the latest reading plus a Chart.js rolling history graph with dashed asymptote reference lines (0 V / 5 V for voltage; 0 µC / 1100 µC for Q at 220 µF × 5 V)
- Indicate current phase (Charging / Discharging) on the page
- Add Condensator nav link across existing dashboard pages
- Add pytest coverage for serial parsing and route

## Capabilities

### New Capabilities

- `condensator-display`: condensator serial ingestion, WebSocket events, and Condensator page UI with voltage and Q graph widgets

### Modified Capabilities

- (none)

## Impact

- **Arduino**: existing `arduino/condensator/condensator.ino` (no firmware changes required for v1)
- **Backend**: `parse_condensator_line()`, phase-line handling, WebSocket `condensator` events, route `/condensator`, status API fields
- **Frontend**: new `static/condensator.html`; nav links on all dashboard pages
- **Tests**: `pytest/test_condensator.py`

## Non-Goals

- Changing capacitor hardware wiring or capacitance constant in firmware
- Server-side persistent history or database storage
- Combining condensator with other sketches on COM8 (one sketch at a time, same as other dashboards)
