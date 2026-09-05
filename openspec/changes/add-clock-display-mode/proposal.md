## Why

The mulie_function display currently supports only a 3-button counter. Users need a second operating mode—a live digital clock—without reflashing firmware, toggled from the same three buttons they already use for reset.

## What Changes

- Add two firmware modes: **counter mode** (existing 3-button digit logic) and **clock mode** (hh:mm with a colon dot).
- Toggle modes by holding the **reset button** (A0) for **3 seconds**.
- Clock starts at **12:00** when first activated and keeps advancing in the background even while counter mode is shown.
- Extend `MultiFunctionDisplay` to render a colon segment between hour and minute digits.
- Add clock math helpers and EpoxyDuino unit tests for time splitting and tick logic.
- Keep the existing short hold (500 ms, all three buttons) as counter reset in counter mode only.
- Emit `Clock: HH:MM` over serial on boot and each minute tick; parse in Python and broadcast via WebSocket.
- Add a **separate read-only clock widget** on the Display dashboard (`/display`) showing live `hh:mm`, distinct from the counter widget.

## Capabilities

### New Capabilities

_(none — behavior extends the existing display capability)_

### Modified Capabilities

- `display-display`: Add dual-mode operation (counter vs clock), 3-second mode toggle, background clock from 12:00, hh:mm colon display format, serial clock ingestion, and a separate dashboard clock widget.

## Impact

- **Firmware**: `arduino/mulie_function/mulie_function.ino`, `MultiFunctionDisplay.{h,cpp}`, new or extended `display_math.h` clock helpers.
- **Tests**: `arduino-tests/test_mulie_function/` — clock math and mode-toggle logic.
- **Web/API**: `main.py` serial parser, WebSocket `clock` events, `GET /api/status` `clock_time` field, `static/display.html` separate clock card.
- **Tests**: `pytest/test_display.py` — clock line parsing, status API, WebSocket cache.
