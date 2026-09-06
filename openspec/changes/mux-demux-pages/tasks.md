## 1. Backend — DEMUX serial

- [x] 1.1 Add `DEMUX_PATTERN` regex and `parse_demux_line()` in `main.py`; verify with unit tests for valid DEMUX lines and invalid lines in `pytest/test_mux_demux.py`
- [x] 1.2 Add `last_demux_*` globals, `notify_demux()`, `broadcast_demux()`, and call from `read_serial()` when a DEMUX line is parsed; verify read-serial test in `pytest/test_mux_demux.py`

## 2. Backend — routes and status API

- [x] 2.1 Add DEMUX fields to `GET /api/status`, replace `GET /combination` with `GET /multiplexor` and `GET /demultiplexor`, and send cached `demux` message on WebSocket connect; verify with tests in `pytest/test_mux_demux.py`

## 3. Frontend — Multiplexor page

- [x] 3.1 Rename `static/combination.html` to `static/multiplexor.html`; update page title to **Multiplexor**, nav labels, and active accent; keep 4-row MUX truth table with X and existing widgets
- [x] 3.2 Update Multiplexor WebSocket/status polling to use `/multiplexor` context only; verify page loads via `GET /multiplexor` test

## 4. Frontend — Demultiplexor page

- [x] 4.1 Create `static/demultiplexor.html` with sidebar layout, rose nav accent (`#fb7185`), four widget cards (A/D4, DI/D2, Y0/D11, Y1/D12), reusing Multiplexor card styling
- [x] 4.2 Wire WebSocket `demux` handler, `/api/status` poll, widget status-dot lifecycle, 4-row DEMUX truth table with X on inactive output, and active-row highlight; verify page loads via `GET /demultiplexor` test

## 5. Navigation

- [x] 5.1 Replace **Combination Devices** link with **Multiplexor** and **Demultiplexor** in sidebar of `static/index.html`, `static/sensors.html`, `static/digital.html`, `static/valves.html`, `static/display.html`, `static/multiplexor.html`, and `static/demultiplexor.html`; verify both links appear on each page

## 6. Tests cleanup

- [x] 6.1 Rename `pytest/test_combination.py` to `pytest/test_mux_demux.py`; update MUX page route tests to `/multiplexor`; add DEMUX parser, status API, and WebSocket cache tests; run `python -m pytest pytest/test_mux_demux.py -q` and confirm all pass

## 7. Manual verification

- [ ] 7.1 Flash `arduino/mux/mux.ino`, open `/multiplexor`, verify MUX widgets and truth-table highlight update every ~2 s
- [ ] 7.2 Flash `arduino/demux/demux.ino`, open `/demultiplexor`, verify DEMUX widgets and truth-table highlight update every ~2 s

## 8. Arduino and CI tests

- [x] 8.1 Add `arduino/demux_logic.h` and `arduino-tests/test_demux/` AUnit tests (4 truth-table cases)
- [x] 8.2 Expand `demux.integration.yaml`; CI Wokwi stage `arduino-integration-tests-wokwi` runs only `WOKWI_SKETCH=demux`
- [x] 8.3 CI runs `pytest/test_mux_demux.py` in dedicated Python step; add demux to `AGENTS.md` and flash-arduino skill
