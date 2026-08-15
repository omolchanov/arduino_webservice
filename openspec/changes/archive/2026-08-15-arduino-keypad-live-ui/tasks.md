## 1. Project setup

- [x] 1.1 Create `requirements.txt` with `fastapi`, `uvicorn[standard]`, `pyserial`
- [x] 1.2 Save Arduino sketch to `arduino/keypad.ino`

## 2. Backend (main.py)

- [x] 2.1 FastAPI app with lifespan: open serial port, start daemon read thread, async queue consumer
- [x] 2.2 Validate keys (`0-9`, `*`, `#`, `A-D`); ignore invalid input
- [x] 2.3 WebSocket endpoint `/ws` — subscribe clients, broadcast `{"key": "..."}`
- [x] 2.4 `GET /` serves `static/index.html` via `FileResponse`
- [x] 2.5 Graceful handling when COM port unavailable (app still starts)

## 3. Frontend (static/index.html)

- [x] 3.1 Self-contained HTML + CSS: last-key display, history list, connection status
- [x] 3.2 WebSocket client connecting to `/ws` with auto-reconnect
- [x] 3.3 On message: update last key and append to history

## 4. Verification

- [x] 4.1 Start app with `uvicorn main:app --reload` and confirm page loads at `http://localhost:8000`
- [x] 4.2 With Arduino connected on COM port, press keys and verify live display
