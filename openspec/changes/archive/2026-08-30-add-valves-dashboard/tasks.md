## 1. Backend parser and state

- [x] 1.1 Add `VALVE_PATTERN` regex and `parse_valve_line()` in `main.py`; verify with unit tests for AND/OR lines and invalid lines in `tests/test_valves.py`
- [x] 1.2 Add `last_valve_a`, `last_valve_b`, `last_valve_y`, `last_valve_gate` globals, `notify_valve()`, `broadcast_valve()`, and call from `read_serial()` when a valve line is parsed; verify read-serial test in `tests/test_valves.py`

## 2. Gate selection API and serial write

- [x] 2.1 Add thread-safe `write_serial_gate(gate)` helper and `POST /api/valve/gate` endpoint (400 for invalid gate, 503 when disconnected); verify with tests in `tests/test_valves.py`

## 3. Status API, route, and WebSocket cache

- [x] 3.1 Add valve fields to `GET /api/status`, `GET /valves` route serving `static/valves.html`, and cached `valve` message on WebSocket connect; verify with tests in `tests/test_valves.py`

## 4. Frontend — Valves page

- [x] 4.1 Create `static/valves.html` with sidebar layout, violet nav accent (`#a78bfa`), topbar with gate dropdown (AND/OR) left of status badge, and three widget cards (selected gate, inputs A/B, output Y) reusing Digital page card styling
- [x] 4.2 Wire WebSocket `valve` handler, `/api/status` poll, widget status-dot lifecycle, dropdown `POST /api/valve/gate` with custom toast notifications, and truth table with row highlight for current A/B

## 5. Navigation

- [x] 5.1 Add `<a href="/valves">Valves</a>` to sidebar in `static/index.html`, `static/sensors.html`, and `static/digital.html`

## 6. Manual verification

- [x] 6.1 Flash `arduino/valves.ino`, close Serial Monitor, restart uvicorn (release COM8), open `/valves`, press buttons A/B to verify widgets and truth table highlight update live; switch dropdown AND ↔ OR to verify gate changes on Arduino
