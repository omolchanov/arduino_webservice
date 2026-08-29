## 1. Backend parser and broadcasts

- [x] 1.1 Add `parse_simple01_line()` regex capturing Generated, Potentiometer V, and Detected from full `simple01.ino` lines; verify unit tests pass for sample HIGH/LOW lines and invalid lines return `None`
- [x] 1.2 Add `last_potentiometer_v` / `last_detected_value` state, `notify_potentiometer` / `notify_detected`, and WebSocket broadcasts `{"type": "potentiometer", "v": ...}` and `{"type": "detected", "value": ...}`; verify `read_serial()` emits all three events from one parsed line
- [x] 1.3 Extend `GET /api/status` with `last_potentiometer_v` and `last_detected_value`; verify response JSON includes both fields after a parsed line
- [x] 1.4 Send cached potentiometer and detected values on WebSocket connect when available; verify new client receives both with `"cached": true`

## 2. Digital dashboard UI

- [x] 2.1 Add **Potentiometer** card to `static/digital.html` (status dot, large value, `V` unit) reusing Sensors `.distance-value` / `.distance-unit` styling; verify layout shows card in dashboard grid
- [x] 2.2 Add **Detected logic LED** card (status dot, large `0`/`1`, `detected` label); verify layout shows card beside Potentiometer
- [x] 2.3 Wire WebSocket handlers and `/api/status` seeding for `potentiometer` and `detected` events with status-dot lifecycle; verify widgets update live when Arduino sends serial data
- [x] 2.4 Confirm Logic signal LED card (graph, Clear button, localStorage history) is unchanged; verify existing logic graph still updates on `Generated` values only

## 3. Integration verification

- [x] 3.1 Upload `arduino/simple01.ino`, start uvicorn, open `/digital`, and verify potentiometer voltage and detected 0/1 update every second while Logic signal LED graph continues to toggle between 0 and 1
