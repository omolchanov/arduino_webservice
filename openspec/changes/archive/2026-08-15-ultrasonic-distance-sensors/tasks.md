## 1. Arduino sketch

- [x] 1.1 Save distance sensor sketch to `arduino/distance.ino` (TRIG=9, ECHO=10)

## 2. Backend

- [x] 2.1 Add `parse_distance_line()` for `Distance: X cm` format
- [x] 2.2 Rename `read_keys()` to `read_serial()`; broadcast distance events and queue keys
- [x] 2.3 Track `last_distance_cm`; send on WebSocket connect
- [x] 2.4 Add `GET /sensors` route serving `static/sensors.html`

## 3. Frontend

- [x] 3.1 Create `static/sensors.html` with Distance section, status label, WebSocket client
- [x] 3.2 Add nav links (Keypad | Sensors) on `index.html` and `sensors.html`
- [x] 3.3 Reuse existing dark theme and notification styles

## 4. Verification

- [x] 4.1 Upload `distance.ino`, start server, open `/sensors` — distance updates live
