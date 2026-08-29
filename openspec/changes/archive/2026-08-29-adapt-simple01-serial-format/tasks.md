## 1. Backend serial parsers

- [x] 1.1 Add `parse_signal_pin_line()` for `SIGNAL_PIN: Logic 0|1` lines and verify unit tests pass for HIGH/LOW and invalid lines
- [x] 1.2 Add `parse_pot_line()` for `Pot: X.XX V | Logic: 0|UNDEFINED|1` (optional PWM suffix) and verify unit tests pass mapping UNDEFINED → `0.5`
- [x] 1.3 Update `read_serial()` to dispatch signal-pin → `notify_logic`, pot → `notify_potentiometer` + `notify_detected`; remove old `SIMPLE01_PATTERN` / `parse_simple01_line()`
- [x] 1.4 Update `test_read_serial_simple01.py` and verify SIGNAL_PIN emits logic only and Pot line emits pot + detected (`0.5` for UNDEFINED)

## 2. Frontend Digital dashboard

- [x] 2.1 Update detected value card and `handleDetected` to display `0`, `0.5`, `1` and verify WebSocket `detected` events update the widget
- [x] 2.2 Update detected history chart Y-axis to ticks `0`, `0.5`, `1` (stepped line) and verify points plot at all three values
- [x] 2.3 Replace pot transition markers with dashed zone boundary lines at 1.5 V (green) and 3.0 V (red)
- [x] 2.4 Verify `/api/status` seeds `last_detected_value: 0.5` into widget on page load

## 3. Verification

- [x] 3.1 Run `python -m unittest tests.test_parse_simple01 tests.test_read_serial_simple01` and verify all tests pass
- [x] 3.2 Manual smoke test with `simple01.ino` on COM8: confirm logic graph, pot widget, detected widget, and zone lines update live on `/digital`
