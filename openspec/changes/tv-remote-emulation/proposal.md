## Why

The project already covers keypad, sensors, valves, and combinational logic dashboards, but there is no way to experiment with an infrared TV remote and see decoded button presses in the browser. A dedicated TV-remote sketch and dashboard lets users wire an IR receiver, point a common remote at it, and watch live key events on a TV-themed page—matching the one-sketch-per-page pattern used elsewhere.

## What Changes

- Add new Arduino sketch `arduino/tv_remote/tv_remote.ino` that decodes IR signals from a receiver module and prints labeled key lines over serial (9600 baud)
- Add shared logic header `arduino/tv_remote_logic.h` and AUnit tests in `arduino-tests/test_tv_remote/` for button-name mapping
- Add TV Remote dashboard at `GET /tv-remote` (`static/tv_remote.html`) showing the last pressed key prominently, a scrolling history list, and optional raw code display
- Add serial parsing, WebSocket `remote` events, status API fields (`last_remote_key`, `last_remote_code`), and cached state on WebSocket connect in `main.py`
- Add **TV Remote** nav link to sidebar on all dashboard pages
- Add pytest coverage for parser, route, status API, and WebSocket cache

## Capabilities

### New Capabilities

- `tv-remote-display`: IR remote serial ingestion from `tv_remote.ino`, TV Remote dashboard with live key display and history

### Modified Capabilities

<!-- None — keypad and other dashboards are unchanged; this is a new sketch and page -->

## Impact

- **Arduino**: new `arduino/tv_remote/` sketch; optional Wokwi integration files; `arduino-cli lib install "IRremote"` (or equivalent) for CI compile
- **Backend**: `main.py` — remote parser, `notify_remote` / WebSocket `remote` events, `/tv-remote` route, status API fields
- **Frontend**: new `static/tv_remote.html`; nav updates in all `static/*.html`
- **Tests**: `pytest/test_tv_remote.py`; `arduino-tests/test_tv_remote/`
- **Docs**: `AGENTS.md` sketch table entry

## Non-Goals

- Actually driving a physical TV or HDMI output
- Learning or storing custom remote protocols beyond a fixed NEC-style mapping for a common remote
- Browser control of Arduino (read-only dashboard, like sensors/mux)
- Combining TV-remote firmware with other sketches in one upload
