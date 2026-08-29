## 1. Backend parser and state

- [x] 1.1 Extend `POT_PATTERN` and `parse_pot_line()` in `main.py` to return `(pot_v, detected, current_ma, resistance_ohm)` and verify `tests/test_parse_simple01.py` passes for legacy lines, current-only lines, and full lines with `LED Resistance`
- [x] 1.2 Add `last_led_resistance_ohm`, `notify_resistance()`, `broadcast_resistance()`, and call `notify_resistance` from `read_serial()` when `resistance_ohm` is not None; verify `tests/test_read_serial_simple01.py` passes

## 2. Status API and WebSocket cache

- [x] 2.1 Add `last_led_resistance_ohm` to `GET /api/status` and send cached `resistance` message on WebSocket connect; verify `tests/test_digital_api.py` passes

## 3. Frontend — live resistance widget

- [x] 3.1 Add Resistance card to `static/digital.html` after the Current card (header + status dot + value + **Ω** unit) reusing current card styling with orange accent `#f97316`
- [x] 3.2 Register `widgets.resistance` for status-dot lifecycle and wire `handleResistance()` from WebSocket and `pollStatus` seeding from `last_led_resistance_ohm`

## 4. Frontend — resistance history chart

- [x] 4.1 Add Resistance history wide card immediately after the mA history card with Chart.js line chart (Y-axis 0–2000 Ω, 120s rolling window, localStorage key `digital-resistance-history`)
- [x] 4.2 Include resistance history in Clear button, `beforeunload` save, and initial render from localStorage

## 5. Manual verification

- [x] 5.1 Flash `arduino/simple01.ino`, close Serial Monitor, restart uvicorn (release COM8), open `/digital`, and verify potentiometer, detected, current, and resistance widgets all update live including resistance history graph placed after mA history
