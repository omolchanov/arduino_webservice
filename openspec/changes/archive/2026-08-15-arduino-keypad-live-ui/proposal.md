## Why

An Arduino Uno with a 4x4 matrix keypad sends key presses over USB serial. We need a simple way to see those keys live in a browser without a separate bridge script or heavy architecture.

## What Changes

- Minimal FastAPI app that reads serial input in a background thread
- WebSocket endpoint to push each key to connected browsers in real time
- Single self-contained HTML page showing the last pressed key and recent history
- Arduino sketch saved as reference (`arduino/keypad.ino`)

## Capabilities

### New Capabilities

- `keypad-display`: Serial ingestion, WebSocket broadcast, and live browser UI for keypad input

### Modified Capabilities

_(none — greenfield project)_

## Impact

- **New files**: `main.py`, `requirements.txt`, `static/index.html`, `arduino/keypad.ino`
- **Dependencies**: `fastapi`, `uvicorn[standard]`, `pyserial`
- **Hardware**: Arduino Uno on Windows COM port (default `COM3`)
- **Non-goals**: MVC structure, database, REST API, PIN entry flow, authentication
