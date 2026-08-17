## 1. Arduino sketches

- [x] 1.1 Save LDR sketch to `arduino/light.ino` (A0, inverted ADC, `Light: <value>`, `delay(1000)`)
- [x] 1.2 Update `arduino/distance.ino` — change `delay(500)` to `delay(1000)`

## 2. Backend

- [x] 2.1 Add `LIGHT_PATTERN` and `parse_light_line()` for `Light: <integer>` format
- [x] 2.2 Track `last_light_level`; broadcast light events in `read_serial()`
- [x] 2.3 Add `broadcast_light()` and send last value on WebSocket connect
- [x] 2.4 Add `last_light_level` to `GET /api/status` response

## 3. Frontend

- [x] 3.1 Add **Lighting level** card on `static/sensors.html` (reuse card/value styles)
- [x] 3.2 Handle WebSocket `light` events and `last_light_level` from status poll

## 4. Verification

- [x] 4.1 Upload `light.ino`, start server, open `/sensors` — lighting level updates live
