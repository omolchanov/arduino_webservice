## Why

An LM35 temperature sensor is connected to Arduino analog pin A3. The combined `arduino/sensors/sensors.ino` sketch converts the ADC reading to degrees Celsius and publishes `Temperature: <value> C` over serial every five seconds. The Sensors dashboard should show this live reading alongside the existing Distance and Lighting level widgets.

## What Changes

- Confirm LM35 support in `arduino/sensors/sensors.ino` (A3, voltage conversion, `Temperature: <value> C` line)
- Extend `main.py` serial parser to handle temperature lines and broadcast via WebSocket
- Add **Temperature** card on the Sensors page (`/sensors`) showing the latest value in °C with a per-sensor status dot
- Expose `last_temperature_c` in `GET /api/status` for initial page load and WebSocket connect snapshot

## Capabilities

### Modified Capabilities

- `sensors-display`: LM35 temperature ingestion and Temperature widget on Sensors page

## Impact

- **Arduino**: `arduino/sensors/sensors.ino` — LM35 on A3 (already present in sketch)
- **Backend**: `parse_temperature_line()`, temperature WebSocket events, `last_temperature_c` in status API
- **Frontend**: new Temperature card on `static/sensors.html` with status-dot logic matching Distance and Lighting level

## Non-Goals

- Separate single-sensor firmware sketches for temperature
- Storing temperature history or charts
- Fahrenheit display or user-selectable units
