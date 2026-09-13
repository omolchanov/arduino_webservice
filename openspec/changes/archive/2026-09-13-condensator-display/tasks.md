## 1. Backend — condensator serial ingestion

- [x] 1.1 Add `parse_condensator_line()` in `main.py` matching `V = <v> V   Q = <q> uC` and verify it returns `(v, q_uc)` for valid lines and `None` otherwise
- [x] 1.2 Add phase-line handling for `Charging...` / `Discharging...`, `last_condensator_v`, `last_condensator_q_uc`, `last_condensator_phase`, `notify_condensator()` / `notify_condensator_phase()`, wire into `read_serial()`, and verify WebSocket broadcasts `{"type": "condensator", ...}` and `{"type": "condensator_phase", ...}`
- [x] 1.3 Extend `GET /api/status` and WebSocket connect snapshot with `last_condensator_v`, `last_condensator_q_uc`, `last_condensator_phase` and verify response includes the fields

## 2. Backend — Condensator route

- [x] 2.1 Add `GET /condensator` route serving `static/condensator.html` and verify `pytest/test_condensator.py::test_condensator_page` passes

## 3. Frontend — Condensator dashboard

- [x] 3.1 Create `static/condensator.html` with Sensors/Digital-style layout (sidebar, topbar, dark cards, custom notifications) and sky-blue nav accent
- [x] 3.2 Add **Voltage** widget: large V value, Chart.js rolling history (~120 points), dashed asymptote lines at 0 V and 5 V
- [x] 3.3 Add **Charge Q** widget: large µC value, Chart.js rolling history, dashed asymptote lines at 0 µC and 1100 µC
- [x] 3.4 Add phase badge (Charging / Discharging), Clear history button, WebSocket handlers, and `/api/status` polling (3s) for live updates and Online/Offline badge

## 4. Navigation

- [x] 4.1 Add **Condensator** nav link to all dashboard pages (`index.html`, `sensors.html`, `digital.html`, `valves.html`, `display.html`, `multiplexor.html`, `demultiplexor.html`) and verify each page links to `/condensator`

## 5. Tests and docs

- [x] 5.1 Add `pytest/test_condensator.py` for parser unit tests and route test; verify `python -m pytest pytest/test_condensator.py` passes
- [x] 5.2 Add `arduino/condensator/` to AGENTS.md sketch table and verify entry documents one-sketch-per-dashboard constraint

## 6. Manual verification

- [x] 6.1 Upload `arduino/condensator/condensator.ino`, close Serial Monitor, run `uvicorn main:app --reload`, open `/condensator`, and verify voltage rises toward 5 V during Charging then falls toward 0 V during Discharging with Q tracking C×V and asymptote lines visible on both graphs
