## Context

The Sensors page (`static/sensors.html`) already shows two cards — **Distance** and **Lighting level** — with a global **Online** / **Offline** badge in the top bar driven by `serial_status` WebSocket events and `/api/status`. Sensor values arrive via WebSocket (`distance`, `light`) or the status poll (`last_distance_cm`, `last_light_level`). The combined firmware publishes both lines every five seconds.

## Goals / Non-Goals

**Goals:**

- Small coloured dot immediately to the right of each card header label
- **Grey** on page load (initializing) until status is resolved
- **Green** when that sensor has received at least one valid reading while Arduino is online
- **Red** when Arduino is offline, or online but that sensor has not delivered data within a timeout
- Reuse existing dark-theme colours consistent with `.app-status` (green `#4ade80`, red `#f87171`, grey `#888`)

**Non-goals:**

- Backend changes or new API fields
- Tooltips, labels, or accessibility text beyond colour (can add `title` attribute optionally)
- Historical uptime or reconnect counters

## Decisions

### 1. Dot placement and styling

Add a `<span class="sensor-status-dot">` inside `.card-header`, after the sensor name text:

```html
<div class="card-header">
  Distance <span class="sensor-status-dot initializing" aria-hidden="true"></span>
</div>
```

CSS: 8px circle, `display: inline-block`, `margin-left: 0.4rem`, `vertical-align: middle`.

| Class | Colour |
|-------|--------|
| `.initializing` | `#888` (grey) |
| `.ok` | `#4ade80` (green) |
| `.error` | `#f87171` (red) |

### 2. Per-sensor state machine

Each sensor (`distance`, `light`) tracks:

- `hasData` — boolean, set true on first valid reading
- `dotState` — `initializing` | `ok` | `error`

**Rules:**

| Condition | Dot |
|-----------|-----|
| Page load, Arduino status unknown | grey |
| `serial_connected === false` | red (all sensors) |
| `serial_connected === true`, no reading yet, within timeout | grey |
| `serial_connected === true`, reading received | green |
| `serial_connected === true`, timeout elapsed, no reading | red |

### 3. Timeout for "no data"

Firmware publishes every **5 seconds**. Use a **10 second** client-side timeout after Arduino goes online before marking a sensor without data as red. Reset timeout timers when `serial_status.connected` flips to `true`. Clear `hasData` when Arduino disconnects so dots return to red (not grey) while offline.

### 4. Data sources (unchanged)

Treat these as valid "data received" for the respective sensor:

| Sensor | WebSocket | Status poll |
|--------|-----------|-------------|
| Distance | `type: "distance"`, `cm != null` | `last_distance_cm != null` |
| Light | `type: "light"`, `level != null` | `last_light_level != null` |

On `pollStatus()` and WebSocket handlers, call a shared `markSensorOk("distance")` / `markSensorOk("light")` helper.

### 5. Arduino offline overrides all

When `setStatus(false)` runs (WebSocket `serial_status` disconnected, poll failure, or `ws.onclose`):

- Set every sensor dot to **red** immediately
- Clear per-sensor `hasData` flags
- Cancel pending timeout timers

When `setStatus(true)`:

- Sensors without cached data start **grey**, timers restart
- Sensors with values from poll snapshot go **green** immediately

## Architecture

```
serial_status (connected?)
        ↓
  offline → all dots red
  online  → per-sensor timers + data events
                ↓
         distance/light WS or poll
                ↓
         markSensorOk → green dot
                ↓
         10s timeout, no data → red dot
```

## Risks / Trade-offs

- **[Trade-off] Client-only health** → dot reflects what the browser sees, not server-internal parser state; acceptable for this UI
- **[Risk] Slow firmware** → 10s timeout is 2× the 5s publish interval; avoids false red on first cycle
