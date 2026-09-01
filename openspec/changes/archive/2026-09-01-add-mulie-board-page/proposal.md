## Why

The mulie function board (`arduino/mulie_function/`) is currently exposed through a generic "Display" dashboard. Users need a clearly named **Mulie Board** page where the UI reflects the **live state read from the device**—the 3 digits entered on the physical buttons (or reset on the board)—and also supports remote set/reset, using the same patterns as the Valves dashboard.

## What Changes

- Add a **Mulie Board** dashboard at `GET /mulie` (`static/mulie.html`) for managing the mulie function board
- Replace sidebar nav label "Display" with **Mulie Board** on all pages; link to `/mulie`
- Add `POST /api/display/reset` to send `RESET\n` to the Arduino (firmware already supports `R` / `RESET`)
- Mulie Board page widgets: **board-sourced** live 3-digit value (000–999) updated from serial `Display: <n>` when buttons are pressed on the device; numeric input + Set; Reset button; online/offline status; custom toast notifications
- Remove the old Display page route (`GET /display`) and `static/display.html` (**BREAKING** for bookmarks to `/display`)
- Update `display-display` spec: correct button pins (A1/A2/A3), Mulie Board page requirements, reset API

## Capabilities

### New Capabilities

<!-- None — extends existing display-display capability -->

### Modified Capabilities

- `display-display`: Rename dashboard from Display to Mulie Board (`/mulie`), require UI to show board-read digit state, add reset API and reset UI, update button pin table to match firmware (A1/A2/A3), remove `/display` route requirement

## Impact

- **Backend**: `main.py` — add `/mulie` route, `POST /api/display/reset`, remove `/display` route
- **Frontend**: new `static/mulie.html`; update nav in `index.html`, `sensors.html`, `digital.html`, `valves.html`; delete `static/display.html`
- **Tests**: update `pytest/test_display.py` for new route and reset endpoint
- **Specs**: delta update to `openspec/specs/display-display/spec.md`
- **Arduino**: no firmware changes required (reset serial command already implemented)
