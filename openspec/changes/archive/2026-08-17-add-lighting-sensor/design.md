## Context

The LDR sketch sends lines like `Light: 512` over serial at 9600 baud every 1 second. The value is already inverted on the Arduino (`1023 - analogRead(A0)`), so higher numbers mean more light. The existing Sensors page shows distance from a separate sketch; both message types share one serial connection and one WebSocket endpoint. Only one Arduino sketch runs at a time.

## Goals / Non-Goals

**Goals:**

- Save LDR sketch to `arduino/light.ino` (user-provided, A0, inverted reading, 1s interval)
- Set sensor read interval to 1s in all sensor sketches (`light.ino`, `distance.ino`)
- Parse `Light: <integer>` in Python
- Broadcast `{"type": "light", "level": <int>}` over WebSocket
- Add **Lighting level** card on `static/sensors.html` next to Distance
- Track `last_light_level`; include in `/api/status` and WebSocket connect snapshot

**Non-goals:**

- Merging distance + light into one firmware
- Converting ADC to lux or percentage
- REST polling beyond existing status poll

## Decisions

### 1. Serial parser

Add `parse_light_line(line) -> int | None`:

| Input | Result |
|-------|--------|
| `Light: 512` | `512` |
| `Light: 0` | `0` |
| `Light: 1023` | `1023` |
| Other lines | delegate to existing distance/key parsers |

In `read_serial()`, check light lines after distance, before keys.

### 2. WebSocket messages

```json
{"type": "light", "level": 512}
```

On connect, send last known light level if available (in-memory `last_light_level`).

### 3. Status API

Extend `GET /api/status` response:

```json
{
  "serial_connected": true,
  "com_port": "COM8",
  "ws_clients": 1,
  "last_distance_cm": 42.5,
  "last_light_level": 512
}
```

### 4. Sensors page UI

- Reuse existing card layout and `.distance-value` styling for the light widget
- Card header: **Lighting level**
- Large integer display (no unit label — raw inverted ADC)
- Handle WebSocket `light` events and status poll `last_light_level`

### 5. Arduino sketches — 1 second read interval

Sensor data SHALL be sampled and published once per second. Enforce this in firmware with `delay(1000)` at the end of each sensor sketch's `loop()`:

**`arduino/light.ino`** (new):

- `LDR_PIN` = A0
- Invert: `light = 1023 - analogRead(LDR_PIN)`
- Output: `Light: <value>` with `delay(1000)`

**`arduino/distance.ino`** (update):

- Change `delay(500)` → `delay(1000)` so distance readings match the same 1s cadence

## Architecture

```
Arduino (light.ino) → Serial "Light: 512"
                              ↓
                     parse_light_line()
                              ↓
                     WebSocket broadcast
                              ↓
                     static/sensors.html (Lighting level card)
```

## Risks / Trade-offs

- **[Risk] COM port mismatch** → user sets `COM_PORT` in `main.py`
- **[Trade-off] One sketch at a time** → user uploads `light.ino` or `distance.ino`; server handles both formats on the same port
