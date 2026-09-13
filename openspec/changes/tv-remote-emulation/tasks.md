## 1. Arduino firmware

- [x] 1.1 Create `arduino/tv_remote_logic.h` with `remoteLabelForCode(uint32_t code)` mapping common NEC codes to labels (POWER, 0–9, VOL+, VOL-, CH+, CH-, MUTE, INPUT, etc.) and verify with AUnit tests in `arduino-tests/test_tv_remote/`
- [x] 1.2 Create `arduino/tv_remote/tv_remote.ino` using IRremote on D2, print `Remote: <label>` or `Remote: UNKNOWN (0x…)` on decode, print `Remote ready` on boot, debounce repeat codes within 300 ms, and verify `arduino-cli compile --fqbn arduino:avr:uno arduino/tv_remote` succeeds

## 2. Backend — serial parsing

- [x] 2.1 Add `REMOTE_PATTERN`, `parse_remote_line()`, `last_remote_key` / `last_remote_code` globals, `notify_remote()`, and `broadcast_remote()` in `main.py`; verify parser unit tests in `pytest/test_tv_remote.py` for known labels, unknown hex, and invalid lines
- [x] 2.2 Wire `read_serial()` to call remote parser before keypad fallback; verify read-serial integration test in `pytest/test_tv_remote.py`

## 3. Backend — routes and status API

- [x] 3.1 Add `last_remote_key` and `last_remote_code` to `GET /api/status`, add `GET /tv-remote` route, and send cached `remote` message on WebSocket connect; verify with tests in `pytest/test_tv_remote.py`

## 4. Frontend — TV Remote page

- [x] 4.1 Create `static/tv_remote.html` with sidebar layout, sky accent (`#38bdf8`), **Last Button** card, **Recent Buttons** history (max 50), raw hex subtext for unknown codes, and page subtitle noting `tv_remote.ino` requirement; verify `GET /tv-remote` returns 200 in pytest
- [x] 4.2 Wire WebSocket handler for `type: "remote"`, `/api/status` poll for serial connection, custom `showNotification()` toasts (no `alert()`), and verify live key updates when serial events are mocked in tests or manual check

## 5. Navigation

- [x] 5.1 Add **TV Remote** link (`/tv-remote`) to sidebar of all `static/*.html` pages; verify link appears on Keypad, Sensors, Digital, Valves, Display, Multiplexor, and Demultiplexor pages

## 6. Tests and docs

- [x] 6.1 Add `arduino-tests/test_tv_remote/Makefile` and register sketch in `AGENTS.md`; run `make -C arduino-tests runtests` (or targeted test) and confirm AUnit pass
- [x] 6.2 Run `python -m pytest pytest/test_tv_remote.py -q` and confirm all pass; add IRremote to CI compile step if not already installed

## 7. Manual verification

- [ ] 7.1 Wire IR receiver to D2, flash `arduino/tv_remote/tv_remote.ino`, open `/tv-remote`, point TV remote at receiver, and verify Last Button and history update for POWER and digit keys
