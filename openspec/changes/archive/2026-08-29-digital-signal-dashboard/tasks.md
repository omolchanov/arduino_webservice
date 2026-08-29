## 1. Backend — logic serial ingestion

- [x] 1.1 Add `parse_logic_line()` in `main.py` matching `Logic 1 (HIGH) - LED ON` / `Logic 0 (LOW) - LED OFF` and verify it returns `1`/`0` for valid lines and `None` otherwise
- [x] 1.2 Add `last_logic_value`, `notify_logic()`, wire into `read_serial()` after light parsing, and verify WebSocket broadcasts `{"type": "logic", "value": 0|1}`
- [x] 1.3 Extend `GET /api/status` and WebSocket connect snapshot with `last_logic_value` and verify response includes the field

## 2. Backend — Digital Signal route

- [x] 2.1 Add `GET /digital` route serving `static/digital.html` and verify `curl http://localhost:8000/digital` returns the page

## 3. Frontend — Digital Signal dashboard

- [x] 3.1 Create `static/digital.html` with Sensors-style layout (sidebar, topbar, dark cards, custom notifications) and amber nav accent
- [x] 3.2 Add Chart.js stepped line graph widget with rolling ~120-point buffer, Y-axis 0–1, and current value display
- [x] 3.3 Wire WebSocket `logic` events and `/api/status` polling (3s) for live graph updates and Online/Offline badge

## 4. Navigation

- [x] 4.1 Add **Digital Signal** nav link to `static/index.html` and `static/sensors.html` and verify all three pages link to each other

## 5. Manual verification

- [x] 5.1 Upload `arduino/simple01.ino` to Arduino, close Serial Monitor, run `uvicorn main:app --reload`, open `/digital`, and verify graph steps between 0 and 1 every second while the LED on D8 toggles ON/OFF in sync
