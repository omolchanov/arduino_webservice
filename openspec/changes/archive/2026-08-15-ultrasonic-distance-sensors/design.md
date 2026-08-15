## Context

The HC-SR04 sensor sketch sends lines like `Distance: 42.50 cm` over serial at 9600 baud every 500ms. The existing app has a Keypad page (`/`) with a serial parser for key presses. Both pages share one serial connection and one WebSocket endpoint. Keypad hardware will be attached later; this change is distance-first.

## Goals / Non-Goals

**Goals:**

- Save distance sketch to `arduino/distance.ino`
- Parse `Distance: <float> cm` in Python
- Broadcast `{"type": "distance", "cm": 42.5}` over WebSocket
- New `static/sensors.html` with Distance display and Connected/Disconnected status
- Simple nav: Keypad | Sensors on both pages

**Non-goals:**

- Keypad wiring or combined firmware
- REST polling (use existing WebSocket)
- MVC refactor

## Decisions

### 1. Serial parser

Add `parse_distance_line(line) -> float | None`:

| Input | Result |
|-------|--------|
| `Distance: 42.50 cm` | `42.5` |
| `Distance: 0.00 cm` | `0.0` |
| Other lines | delegate to existing `parse_key_line()` |

Rename `read_keys()` → `read_serial()`; on distance, broadcast directly; on key, use queue as today.

### 2. WebSocket messages

```json
{"type": "distance", "cm": 42.5}
```

On connect, send last known distance if available (in-memory `last_distance_cm`).

### 3. Sensors page UI

- Match existing dark theme from `index.html`
- Section heading: **Distance**
- Large value display: `42.5 cm`
- Single Connected/Disconnected status (serial link)
- Nav links at top: **Keypad** | **Sensors**

### 4. Routes

| Route | File |
|-------|------|
| `GET /` | `static/index.html` |
| `GET /sensors` | `static/sensors.html` |

Add nav link on keypad page to Sensors.

### 5. Arduino sketch

Use user-provided sketch as-is (`delay(500)`). Pins: TRIG=9, ECHO=10.

## Architecture

```
Arduino (distance.ino) → Serial "Distance: X cm"
                              ↓
                     parse_distance_line()
                              ↓
                     WebSocket broadcast
                              ↓
                     static/sensors.html
```

## Risks / Trade-offs

- **[Risk] COM port mismatch** → user sets `COM_PORT` in `main.py`
- **[Trade-off] Shared WebSocket** → both pages receive all events; each page ignores irrelevant types
