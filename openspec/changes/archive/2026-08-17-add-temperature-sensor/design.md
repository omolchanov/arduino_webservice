## Context

The combined sensor sketch (`arduino/sensors/sensors.ino`) reads HC-SR04 distance, LDR light, and LM35 temperature in one `loop()` cycle, publishing three serial lines plus a separator every five seconds (`delay(5000)`). Temperature is computed on the Arduino:

```
voltage = analogRead(A3) * 5.0 / 1023.0
temperature = voltage * 100.0   // LM35: 10 mV/°C
```

Output format: `Temperature: 23.45 C`

The Sensors page already shows **Distance** and **Lighting level** cards with per-sensor status dots driven by live WebSocket events (cached snapshots update values only, not dot state). Temperature follows the same pattern.

## Goals / Non-Goals

**Goals:**

- Parse `Temperature: <number> C` in Python
- Broadcast `{"type": "temperature", "c": <float>}` over WebSocket
- Track `last_temperature_c`; include in `/api/status` and WebSocket connect snapshot
- Add **Temperature** card on `static/sensors.html` with status dot, value display (1 decimal), and **°C** unit label
- Register `temperature` in the existing `sensors` map and reuse `applySensorReading()` / debounce logic

**Non-goals:**

- Backend or frontend changes to Distance or Lighting level widgets
- Converting to Fahrenheit
- Changing the 5-second firmware publish interval

## Decisions

### 1. Serial parser

Add `TEMPERATURE_PATTERN` and `parse_temperature_line(line) -> float | None`:

| Input | Result |
|-------|--------|
| `Temperature: 23.45 C` | `23.45` |
| `Temperature: 0.00 C` | `0.0` |
| Other lines | delegate to existing distance/light/key parsers |

In `read_serial()`, check temperature lines after light, before keys.

### 2. WebSocket messages

```json
{"type": "temperature", "c": 23.45}
```

On connect, send last known temperature if available:

```json
{"type": "temperature", "c": 23.45, "cached": true}
```

### 3. Status API

Extend `GET /api/status` response:

```json
{
  "serial_connected": true,
  "com_port": "COM8",
  "ws_clients": 1,
  "last_distance_cm": 42.5,
  "last_light_level": 512,
  "last_temperature_c": 23.45
}
```

### 4. Sensors page UI

- Reuse existing `.card`, `.card-header`, `.distance-value`, `.distance-unit`, and `.sensor-status-dot` styles
- Card header: **Temperature** with status dot (`#temperatureDot`)
- Display value to one decimal place; unit label **°C**
- Add `temperature` entry to the `sensors` object alongside `distance` and `light`
- Handle WebSocket `temperature` events and `last_temperature_c` from status poll

### 5. Validity and status dot

Follow the existing per-sensor dot rules from `sensors-display`:

- Dot states: grey (initializing), green (ok), red (error)
- Live WebSocket readings drive dot state; cached snapshots and status poll update displayed value only
- **Valid** temperature: finite number within LM35 range **-55 to 150 °C** (inclusive)
- Debounce green ↔ red transitions by 10 seconds (`SENSOR_PENDING_MS`)
- 10-second init timeout when Arduino comes online with no live reading

### 6. Arduino firmware

`arduino/sensors/sensors.ino` already includes LM35 on `LM35_PIN A3`. No sketch changes required unless the serial line format drifts from `Temperature: <value> C`.

## Architecture

```
Arduino (sensors.ino) → Serial "Temperature: 23.45 C"
                              ↓
                     parse_temperature_line()
                              ↓
                     WebSocket broadcast
                              ↓
                     static/sensors.html (Temperature card + dot)
```

## Risks / Trade-offs

- **[Risk] COM port in use** → close Arduino Serial Monitor before starting uvicorn; release COM8 on server restart/stop
- **[Trade-off] 0 °C is valid** → unlike distance/light, temperature uses range check instead of `> 0` so freezing conditions do not show a false error state
