## 1. Arduino firmware

- [x] 1.1 Verify `arduino/sensors/sensors.ino` reads LM35 on A3 and publishes `Temperature: <value> C` each cycle (user sketch already in place)

## 2. Backend

- [x] 2.1 Add `TEMPERATURE_PATTERN` and `parse_temperature_line()` for `Temperature: <number> C` format
- [x] 2.2 Track `last_temperature_c`; broadcast temperature events in `read_serial()`
- [x] 2.3 Add `broadcast_temperature()` / `notify_temperature()` and send last value on WebSocket connect
- [x] 2.4 Add `last_temperature_c` to `GET /api/status` response

## 3. Frontend

- [x] 3.1 Add **Temperature** card on `static/sensors.html` (reuse card/value/dot styles; unit **°C**)
- [x] 3.2 Register `temperature` in `sensors` map with `isTemperatureValid()` (range -55 to 150 °C)
- [x] 3.3 Handle WebSocket `temperature` events and `last_temperature_c` from status poll

## 4. Verification

- [x] 4.1 Upload `sensors.ino`, start server, open `/sensors` — temperature updates live with green status dot
- [x] 4.2 Confirm dot turns red when Arduino offline; grey → green on reconnect
