## Context

The `arduino/mulie_function/` sketch is already integrated: serial output `Display: <n>`, inbound `S<n>` set, and `R`/`RESET` reset. `main.py` parses display lines, broadcasts WebSocket events, exposes `GET /api/status` and `POST /api/display/value`, and serves `static/display.html` at `/display`. Firmware changes are not required for this work.

See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**

- Serve a Mulie Board management page at `/mulie` where the prominent 3-digit readout is **board-sourced** (serial `Display: <n>` / WebSocket `display` / `display_value` in status)—reflecting digits entered on the physical buttons
- Provide remote set and reset controls alongside the live readout
- Add `POST /api/display/reset` mirroring the existing valve gate write pattern
- Unify sidebar navigation: "Mulie Board" link on every page
- Update tests and spec to match actual button pins (A1/A2/A3)

**Non-Goals:**

- Remote digit increment buttons (hundreds/tens/ones) — physical buttons only unless added later
- Firmware or shift-register changes
- Redirect from `/display` to `/mulie` (clean break; bookmarks must update)
- Renaming API fields (`display_value`, `/api/display/*`) — internal names stay for compatibility

## Decisions

### 1. New page file instead of renaming `display.html`

Create `static/mulie.html` based on `display.html`, update title/copy to "Mulie Board", add Reset button, then delete `display.html`.

**Alternative:** Rename in place — rejected because nav hrefs, route name, and page title all change; a fresh file keeps the diff readable.

### 2. Route `/mulie` with no `/display` redirect

`GET /mulie` serves the new page; remove `GET /display`.

**Alternative:** Keep `/display` as redirect — rejected to avoid two URLs for the same board and to match the "new page" intent.

### 3. Reset API at `POST /api/display/reset`

Add `write_serial_reset()` sending `RESET\n`, following `write_serial_display()` / `write_serial_gate()` conventions. Return `{"ok": true}` on success, HTTP 503 when serial disconnected.

**Alternative:** Reuse `POST /api/display/value` with `{"value": 0}` — rejected because firmware reset also triggers the boot beep and is the explicit serial contract.

### 4. Board state as source of truth for the live widget

The large 3-digit readout is driven exclusively by inbound serial (`Display: <n>`) → WebSocket `display` events and `display_value` on connect/poll. Remote Set/Reset only change the board indirectly; the widget updates when the firmware echoes the new value. Copy/labels on the page SHALL make clear this is the value on the device (e.g. "Live value from board").

**Alternative:** Optimistically update the widget on Set success — rejected because the spec requires reflecting actual board state.

### 5. Keep WebSocket type `display` and status field `display_value`

No protocol rename — only the browser page and nav label change. Reduces churn in `main.py` and existing WebSocket handlers.

### 6. Nav label "Mulie Board" on all static pages

Update `index.html`, `sensors.html`, `digital.html`, `valves.html`, and `mulie.html` sidebar: replace `<a href="/display">Display</a>` with `<a href="/mulie">Mulie Board</a>`.

## Risks / Trade-offs

- **[Risk] Broken bookmarks to `/display`** → Document in proposal as **BREAKING**; no redirect by design.
- **[Risk] Reset returns before Arduino echoes new value** → UI relies on WebSocket `display` event (same as Set); show toast on API success only.
- **[Risk] Serial busy with other sketches** → Page shows offline badge; reset/set return 503 (existing pattern).

## Migration Plan

1. Implement backend: `/mulie` route, `POST /api/display/reset`, remove `/display`
2. Add `static/mulie.html`; update nav on all pages; delete `display.html`
3. Update `pytest/test_display.py` (route + reset tests)
4. On archive: merge spec delta, commit, push

Rollback: restore `/display` route and `display.html` from git; remove reset endpoint.
