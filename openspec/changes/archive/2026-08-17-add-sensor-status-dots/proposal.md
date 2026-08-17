## Why

The Sensors page shows live distance and lighting values but gives no per-sensor health signal. Operators cannot tell at a glance whether each widget is receiving data, still waiting, or failed — especially when Arduino is connected but one sensor line is missing.

## What Changes

- Add a small status dot to the right of each sensor card header (**Distance**, **Lighting level**) on `/sensors`
- Dot states: **grey** (initializing), **green** (data received), **red** (no data or Arduino offline)
- When Arduino serial is offline, force all sensor dots to **red**
- Client-side logic using existing WebSocket events and `/api/status` poll — no new backend endpoints

## Capabilities

### Modified Capabilities

- `sensors-display`: per-sensor status indicator on Sensors page card headers

## Impact

- **Frontend**: `static/sensors.html` — dot markup, CSS, and status state machine per sensor
- **Backend**: none (reuse `serial_status`, `distance`, `light`, and `/api/status`)

## Non-Goals

- Changing the top-right Arduino Online/Offline label
- Per-sensor backend health API or server-side timeouts
- Status dots on the Keypad page
