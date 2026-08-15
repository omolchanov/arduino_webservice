## Context

Arduino Uno scans a 4x4 matrix keypad (rows on pins 2–5, columns on 6–9) and sends one character per line via `Serial.println` at 9600 baud. The Python side must read blocking serial I/O without blocking FastAPI's async event loop, then push keys to browsers over WebSocket.

## Goals / Non-Goals

**Goals:**

- Read serial keys in a background thread and broadcast via WebSocket
- Single `main.py` + `static/index.html` (self-contained HTML/CSS/JS)
- Graceful startup when COM port is busy or Arduino is disconnected
- Save the existing Arduino sketch as `arduino/keypad.ino`

**Non-Goals:**

- MVC architecture, separate bridge script, REST API
- Database persistence, PIN entry flow, authentication
- `.env` configuration (use `COM_PORT` constant in `main.py`)

## Decisions

### 1. Serial reading in a daemon thread

`pyserial` is blocking. On app lifespan startup, open `serial.Serial(COM_PORT, 9600, timeout=1)` and start a daemon thread that reads `readline()`, validates the key, and pushes it into an `asyncio.Queue`. An async consumer task drains the queue and broadcasts to WebSocket clients.

### 2. WebSocket over polling

WebSocket at `/ws` gives sub-100ms updates with no repeated HTTP requests. Connected clients are held in a list; on disconnect they are removed.

### 3. COM port configuration

`COM_PORT = "COM3"` as a module-level constant in `main.py`. User changes it to match Device Manager. Arduino IDE Serial Monitor must be closed before starting Python.

### 4. Valid keys

Match the Arduino `keys[4][4]` matrix: `0123456789*#ABCD`. Reject empty lines and other characters.

### 5. Frontend

Single `static/index.html` with embedded CSS and JS:

- Large last-key display
- Scrolling history (last ~50 keys)
- WebSocket auto-reconnect with status line

## Architecture

```
Arduino Uno → USB Serial (9600) → daemon thread → asyncio.Queue
                                                      ↓
                                              broadcast to /ws clients
                                                      ↓
                                              static/index.html
```

## Risks / Trade-offs

- **[Risk] COM port busy** → Close Serial Monitor before starting; app still runs without serial
- **[Risk] Single process** → Serial and server share one process; acceptable for local dev tool
- **[Trade-off] No REST API** → Cannot inject keys without Arduino; add later if needed

## File layout

```
arduino/
├── main.py
├── requirements.txt
├── static/index.html
├── arduino/keypad.ino
└── openspec/...
```
