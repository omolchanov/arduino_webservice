## 1. Frontend — markup and styles

- [x] 1.1 Add `.sensor-status-dot` CSS with `initializing` (grey), `ok` (green), and `error` (red) states
- [x] 1.2 Add status dot `<span>` to **Distance** and **Lighting level** card headers in `static/sensors.html`

## 2. Frontend — status logic

- [x] 2.1 Implement per-sensor state (`distance`, `light`) with `hasData` flag and dot element references
- [x] 2.2 On valid reading (WebSocket or status poll), call `markSensorOk(sensorId)` to set dot green
- [x] 2.3 On Arduino offline (`setStatus(false)`), set all dots red and reset sensor state
- [x] 2.4 On Arduino online, start 10s timeout per sensor without data; set dot red when timeout fires
- [x] 2.5 On page load poll, apply green immediately if `last_distance_cm` / `last_light_level` are present and Arduino is online

## 3. Verification

- [x] 3.1 Open `/sensors` — dots start grey, then green when data arrives (Arduino online)
- [x] 3.2 Disconnect Arduino — all dots turn red; top bar shows Offline
- [x] 3.3 Reconnect Arduino — dots go grey then green again as readings resume
