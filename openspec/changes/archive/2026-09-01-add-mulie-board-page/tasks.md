## 1. Backend API and routes

- [x] 1.1 Add `write_serial_reset()` in `main.py` that writes `RESET\n` when serial is connected and verify it mirrors `write_serial_display()` error handling
- [x] 1.2 Add `POST /api/display/reset` returning `{"ok": true}` on success and HTTP 503 when disconnected; verify with a unit test
- [x] 1.3 Replace `GET /display` with `GET /mulie` serving `static/mulie.html`; verify `GET /display` returns 404

## 2. Mulie Board frontend

- [x] 2.1 Create `static/mulie.html` from `display.html` with title "Mulie Board", a board-sourced live 3-digit widget (WebSocket `display` + `display_value` on load—no optimistic local override), Set control, and Reset button wired to `POST /api/display/reset` with toast notifications
- [x] 2.2 Update sidebar nav on `index.html`, `sensors.html`, `digital.html`, `valves.html`, and `mulie.html`: replace Display link with `Mulie Board` → `/mulie`; verify all five pages link correctly
- [x] 2.3 Delete `static/display.html` and verify no references to `/display` remain in static files

## 3. Tests

- [x] 3.1 Update `pytest/test_display.py`: change page test to `GET /mulie`, add reset API tests (success, 503 disconnected); run `python -m pytest pytest/test_display.py` and confirm all pass

## 4. Manual verification

- [x] 4.1 With `mulie_function` sketch on COM8, open `/mulie`, press physical buttons and confirm the widget shows the same 3 digits as the 7-segment display without clicking Set
