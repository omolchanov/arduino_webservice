## Why

An HC-SR04 ultrasonic distance sensor is connected to the Arduino (TRIG on D9, ECHO on D10). The webservice needs a dedicated **Sensors** page that shows live distance readings parsed from serial output.

## What Changes

- Add `arduino/distance.ino` sketch that publishes `Distance: <value> cm` every 500ms
- Extend `main.py` serial parser to handle distance lines and broadcast via WebSocket
- Add **Sensors** page at `GET /sensors` with a Distance section showing live readings
- Add simple navigation between Keypad (`/`) and Sensors (`/sensors`)

## Capabilities

### New Capabilities

- `sensors-display`: ultrasonic distance ingestion and live Sensors page UI

### Modified Capabilities

- `keypad-display`: serial read loop generalized to handle multiple message types (keys + distance)

## Impact

- **Arduino**: new `arduino/distance.ino` sketch for HC-SR04 sensor
- **Backend**: `parse_distance_line()`, distance WebSocket events, route `/sensors`
- **Frontend**: new `static/sensors.html`, nav links on both pages

## Non-Goals

- Keypad wiring or combined firmware (keypad attached later)
- Storing distance history in a database
- Charts/graphs
