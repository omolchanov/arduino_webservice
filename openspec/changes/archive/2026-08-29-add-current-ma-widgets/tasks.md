## 1. Backend parser and state

- [x] 1.1 Extend `POT_PATTERN` and `parse_pot_line()` in `main.py` to return `(pot_v, detected, current_ma)` and verify `tests/test_parse_simple01.py` passes for legacy lines, PWM-only lines, and full shunt/current lines
- [x] 1.2 Add `last_current_ma`, `notify_current()`, `broadcast_current()`, and call `notify_current` from `read_serial()` when `current_ma` is not None; verify `tests/test_read_serial_simple01.py` passes

## 2. Status API and WebSocket cache

- [x] 2.1 Add `last_current_ma` to `GET /api/status` and send cached `current` message on WebSocket connect; verify `tests/test_digital_api.py` passes

## 3. Frontend — live current widget

- [x] 3.1 Add Current card to `static/digital.html` (header + status dot + value + `mA` unit) reusing potentiometer card styling with emerald accent `#34d399`
- [x] 3.2 Register `widgets.current` for status-dot lifecycle and wire `handleCurrent()` from WebSocket and `pollStatus` seeding

## 4. Frontend — current history chart

- [x] 4.1 Add Current history wide card with Chart.js line chart (Y-axis 0–500 mA, 120s rolling window, localStorage key `digital-current-history`)
- [x] 4.2 Include current history in Clear button, `beforeunload` save, and initial render from localStorage

## 5. Manual verification

- [ ] 5.1 Flash `arduino/simple01.ino`, close Serial Monitor, restart uvicorn (release COM8), open `/digital`, and verify potentiometer, detected, and current widgets all update live including current history graph
