## Why

An LDR (light-dependent resistor) is connected to Arduino analog pin A0. The sketch inverts the raw ADC reading (`1023 - analogRead`) so higher values mean brighter light, and publishes `Light: <value>` over serial every second. The Sensors dashboard should show this live reading alongside the existing distance widget.

## What Changes

- Add `arduino/light.ino` sketch that reads A0, inverts the value, and sends `Light: <value>` every 1s
- Update `arduino/distance.ino` to publish distance readings every 1s (was 500ms)
- Extend `main.py` serial parser to handle light lines and broadcast via WebSocket
- Add **Lighting level** card on the Sensors page (`/sensors`) showing the latest inverted ADC value
- Expose `last_light_level` in `GET /api/status` for initial page load

## Capabilities

### Modified Capabilities

- `sensors-display`: LDR light-level ingestion and Lighting level widget on Sensors page

## Impact

- **Arduino**: new `arduino/light.ino` sketch for LDR on A0; `arduino/distance.ino` loop interval set to 1s
- **Backend**: `parse_light_line()`, light WebSocket events, `last_light_level` in status API
- **Frontend**: new Lighting level card on `static/sensors.html`

## Non-Goals

- Combined firmware with distance or keypad sketches
- Storing light history or charts
- Physical units (lux/percent) — display raw inverted ADC integer (0–1023)
