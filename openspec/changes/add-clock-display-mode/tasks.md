## 1. Clock math helpers

- [x] 1.1 Add `clock_start_minutes()`, `tick_clock_minutes()`, `minutes_to_hours_minutes()`, and `split_clock_display()` to `arduino/display_math.h` and verify new EpoxyDuino tests pass for 12:00 start, minute tick, and 23:59→00:00 wrap
- [x] 1.2 Extend `arduino-tests/test_mulie_function/test_mulie_function.ino` with clock math tests and verify `make -C arduino-tests/test_mulie_function runtests` passes

## 2. Display colon rendering

- [x] 2.1 Add `showClock(byte hours, byte minutes)` and colon segment rendering on digit index 2 in `MultiFunctionDisplay.{h,cpp}` and verify compile with `arduino-cli compile --fqbn arduino:avr:uno arduino/mulie_function`

## 3. Firmware mode logic

- [x] 3.1 Add `DisplayMode` enum, background clock tick in `loop()`, and refactor `checkResetButtons()` for 500 ms release-reset vs 3000 ms mode toggle in `mulie_function.ino`
- [x] 3.2 Wire mode-specific display refresh (counter vs clock), skip individual button handlers in clock mode, and emit `Clock: HH:MM\n` on each minute tick plus `Mode: counter` / `Mode: clock` on toggle

## 4. Server clock ingestion

- [x] 4.1 Add `parse_clock_line()`, `last_clock_time`, `notify_clock()`, WebSocket broadcast, status field, and cached clock on connect in `main.py`; verify with `python -m pytest pytest/test_display.py -k clock`

## 5. Display dashboard clock widget

- [x] 5.1 Add a separate read-only clock card to `static/display.html` (reuse counter card styling) and wire WebSocket `clock` events plus `clock_time` from status poll

## 6. Verification

- [x] 6.1 Run `make -C arduino-tests/test_mulie_function runtests` and `python -m pytest pytest/test_display.py` and confirm all tests pass
- [ ] 6.2 Manual smoke test: counter widget and clock widget update independently; 3 s hold switches physical display to clock; clock widget advances every minute while counter mode shown on hardware
