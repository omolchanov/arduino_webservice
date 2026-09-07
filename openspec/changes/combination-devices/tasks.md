## 1. Backend parser and state

- [x] 1.1 Add `MUX_PATTERN` regex and `parse_mux_line()` in `main.py`; verify with unit tests for valid MUX lines and invalid lines in `pytest/test_combination.py`
- [x] 1.2 Add `last_mux_a`, `last_mux_di0`, `last_mux_di1`, `last_mux_do` globals, `notify_mux()`, `broadcast_mux()`, and call from `read_serial()` when a MUX line is parsed; verify read-serial test in `pytest/test_combination.py`

## 2. Status API, route, and WebSocket cache

- [x] 2.1 Add MUX fields to `GET /api/status`, `GET /combination` route serving `static/combination.html`, and cached `mux` message on WebSocket connect; verify with tests in `pytest/test_combination.py`

## 3. Frontend — Combination Devices page

- [x] 3.1 Create `static/combination.html` with sidebar layout, emerald nav accent (`#34d399`), topbar with online/offline badge, and four widget cards (address A, data inputs DI0/DI1, output DO/D13) reusing Valves card styling
- [x] 3.2 Wire WebSocket `mux` handler, `/api/status` poll, widget status-dot lifecycle, static 8-row MUX truth table, and active-row highlight when live A/DI0/DI1 match a table row (same pattern as Valves)

## 4. Navigation

- [x] 4.1 Add `<a href="/combination">Combination Devices</a>` to sidebar in `static/index.html`, `static/sensors.html`, `static/digital.html`, `static/valves.html`, and `static/display.html`; verify link appears on each page

## 5. Manual verification

- [x] 5.1 Flash `arduino/mux/mux.ino`, close Serial Monitor, restart uvicorn (release COM8), open `/combination`, change D2/D3/D4 jumpers to verify widgets and truth table highlight update live every ~2 s

## 6. Arduino CI tests

- [x] 6.1 Add mux AUnit tests to CI (`arduino-tests/test_mux`) and Wokwi integration files under `arduino/mux/`; disable Valves integration stage in CI (run mux via `WOKWI_SKETCH=mux`)
