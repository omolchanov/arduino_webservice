---
name: start-app
description: Starts the uvicorn FastAPI server for this Arduino project on http://127.0.0.1:8000 and connects COM8. Use when the user runs /start-app, asks to start or run the server, or restart the app after /stop-app.
---

# Start App

Starts the uvicorn server and connects COM8

## When to use

- User runs `/start-app`
- After `/stop-app` or when the server is not running
- User asks to run `uvicorn main:app --reload`

## Steps

1. If uvicorn is already running, report **http://127.0.0.1:8000** and skip starting a second instance.
2. If restarting, run `/stop-app` first, then continue.
3. Close Arduino Serial Monitor if open (it blocks COM8).
4. Run the start script from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/start-app/scripts/start-app.ps1
```

Or start in a background shell (preferred in Cursor):

```powershell
uvicorn main:app --reload
```

Use `block_until_ms: 0` and wait for `Uvicorn running` or `Serial connected on COM8` in the terminal output.

5. Report URLs:
   - Keypad: http://127.0.0.1:8000/
   - Sensors: http://127.0.0.1:8000/sensors
   - Digital Signal: http://127.0.0.1:8000/digital
6. Note whether COM8 connected or is still retrying.

## Notes

- `COM_PORT` is `COM8` in `main.py`.
- Do not start a second uvicorn if one is already running.
