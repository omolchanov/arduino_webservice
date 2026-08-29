---
name: stop-app
description: Stops the uvicorn FastAPI server for this Arduino project and releases COM8. Use when the user runs /stop-app, asks to stop the server, shut down uvicorn, or release COM8 before uploading a sketch or restarting the app.
---

# Stop App

Stops the uvicorn server and release COM8

## When to use

- User runs `/stop-app`
- Before restarting uvicorn (`uvicorn main:app --reload`)
- Before opening Arduino Serial Monitor or uploading a sketch

## Steps

1. Check the terminals folder for a running `uvicorn main:app` background shell and note its PID.
2. Run the stop script from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/stop-app/scripts/stop-app.ps1
```

Or inline (same behavior):

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'main:app' -or $_.CommandLine -match 'multiprocessing\.spawn.*spawn_main' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
```

3. Confirm no `uvicorn main:app` process remains.
4. Report whether the server was stopped or was not running.

## Notes

- `COM_PORT` is `COM8` in `main.py`; stopping uvicorn closes the serial handle.
- Match only `uvicorn main:app` — do not kill unrelated Python processes.
