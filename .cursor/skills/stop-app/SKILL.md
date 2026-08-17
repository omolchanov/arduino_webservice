---
name: stop-app
description: >-
  Stops the FastAPI uvicorn server and releases COM8 for the Arduino keypad
  project. Use when the user runs /stop-app, asks to stop the server, stop
  uvicorn, shut down the app, or release COM8 before uploading a sketch or
  opening Serial Monitor.
disable-model-invocation: true
---

# Stop App

Stops `uvicorn main:app` and releases **COM8** so the Arduino port is free.

## When to use

- User invokes `/stop-app`
- User asks to stop the server, stop uvicorn, or release COM8
- Before restarting the server or uploading an Arduino sketch

## Steps

1. **Run the stop script** from the project root:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .cursor/skills/stop-app/scripts/stop-app.ps1
   ```

2. **Confirm** output shows port **8000** is free and COM8 should be released.

3. If COM8 is still busy, remind the user to close **Arduino Serial Monitor** or any other app using COM8.

## Notes

- `COM_PORT` is **COM8** in `main.py` (see `AGENTS.md`).
- Killing uvicorn ends the serial thread via FastAPI lifespan shutdown; the script waits briefly for the handle to release.
- Do not start uvicorn again unless the user asks.

## Failure handling

- If the script exits with code **1**, port 8000 may still be in use — report which PIDs remain and retry once.
- If COM8 stays locked after a clean stop, the blocker is usually Serial Monitor, not uvicorn.
