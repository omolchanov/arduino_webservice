## Why

The `arduino/mulie_function/` sketch currently hardcodes `1234` on the 7-segment display with no user input. We need a 3-button counter that starts at **000**, where each button independently increments one digit (0–9, wrapping), plus project integration (serial + dashboard) so the value is visible and controllable from the browser.

## What Changes

- Extend the sketch with **3 buttons** (left / middle / right) that increment the hundreds, tens, and ones digits respectively (0→9, wrap to 0)
- Start display at **000** on boot (value `0`, fourth digit unused / always 0)
- Add debounced `INPUT_PULLUP` button handling (same pattern as `simple01.ino` / `valves.ino`)
- Extract testable digit helpers (`increment_digit`, value ↔ digits) into `display_math.h`
- Rename sketch to `mulie_function.ino`, add serial output `Display: <n>` (0–999) on value change
- Add serial parsing, WebSocket broadcast, status API, and `POST /api/display/value` in `main.py`
- Add **Display** dashboard at `GET /display` showing the live 3-digit value (000–999)
- Add EpoxyDuino unit tests and pytest coverage

## Capabilities

### New Capabilities

- `display-display`: 3-button 7-segment counter firmware, serial ingestion, value-set API, Display dashboard, and live value widget

### Modified Capabilities

<!-- None — Keypad, Sensors, Digital Signal, and Valves specs are unchanged -->

## Impact

- **Arduino**: `arduino/mulie_function/` — button pins D2/D3/D5, counter logic, serial protocol, `display_math.h`
- **Backend**: `main.py` — display parser (0–999), WebSocket, status API, `/display` route
- **Frontend**: new `static/display.html`; nav updates on existing pages
- **Tests**: `pytest/test_display.py`; `arduino-tests/test_mulie_function/`
- **Docs**: update `AGENTS.md` production sketch table

## Non-Goals

- Changing shift-register wiring or segment/digit maps
- Fourth-digit input (display shows 0xx–9xx range only; leading digit of 4-digit hardware stays 0)
- Animations, scrolling text, or decimal-point support
- Combining display firmware with other sketches
