## 1. Arduino shared logic and counter

- [x] 1.1 Create `arduino/display_math.h` with `increment_digit(byte &d)` (wrap 0–9) and `rebuild_counter(byte h, byte t, byte o) -> int` (0–999); verify EpoxyDuino tests in `arduino-tests/test_mulie_function/` pass
- [x] 1.2 Refactor `MultiFunctionDisplay::show()` to clamp 0–9999 (unchanged) and use shared digit logic if applicable; verify compile

## 2. Arduino sketch — 3-button counter

- [x] 2.1 Rename `sketch_sep1a.ino` to `mulie_function.ino`, define button pins D2/D3/D5 as `INPUT_PULLUP`, boot with `counter = 0` and `display.show(0)` showing **000**; verify compile with `arduino-cli compile arduino/mulie_function/`
- [x] 2.2 Add debounced button handlers: left → hundreds, middle → tens, right → ones (each 0–9 wrap); verify on hardware that pressing left on `005` shows `105` and `900` wraps to `000`
- [x] 2.3 Add `Serial.begin(9600)`, emit `Display: <n>` on value change, and parse `S<n>` serial set command (clamp 0–999); verify Serial Monitor shows updates on button press

## 3. Backend parser and state

- [x] 3.1 Add `DISPLAY_PATTERN` regex and `parse_display_line()` in `main.py` (0–999); verify with unit tests in `pytest/test_display.py`
- [x] 3.2 Add `last_display_value` global, `notify_display()`, `broadcast_display()`, and call from `read_serial()`; verify read-serial test in `pytest/test_display.py`

## 4. Set value API and serial write

- [x] 4.1 Add thread-safe `write_serial_display(value)` and `POST /api/display/value` (400 for out-of-range 0–999, 503 when disconnected); verify with tests in `pytest/test_display.py`

## 5. Status API, route, and WebSocket cache

- [x] 5.1 Add `display_value` to `GET /api/status`, `GET /display` route, and cached `display` message on WebSocket connect; verify with tests in `pytest/test_display.py`

## 6. Frontend — Display page

- [x] 6.1 Create `static/display.html` with sidebar, 3-digit zero-padded readout (000–999), number input + Set button; reuse existing dashboard styling
- [x] 6.2 Wire WebSocket `display` handler, `/api/status` poll, `POST /api/display/value` with custom toast notifications

## 7. Navigation and docs

- [x] 7.1 Add `<a href="/display">Display</a>` to sidebar in `static/index.html`, `static/sensors.html`, `static/digital.html`, `static/valves.html`, and `static/display.html`
- [x] 7.2 Add `arduino/mulie_function/` to production sketch table in `AGENTS.md`

## 8. Manual verification

- [ ] 8.1 Flash `mulie_function.ino`, verify boot shows 000 and all three buttons increment/wrap correctly; then open `/display` via uvicorn and verify live updates and Set button
