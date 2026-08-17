---
name: /stop-app
id: stop-app
category: Workflow
description: Stop uvicorn and release COM8 for Arduino
---

Stop the FastAPI uvicorn server and release **COM8**.

## Steps

1. Run from the project root:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .cursor/skills/stop-app/scripts/stop-app.ps1
   ```

2. Confirm port **8000** is free and report the result to the user.

3. If COM8 may still be locked, remind the user to close **Arduino Serial Monitor**.

## Guardrails

- Do not restart uvicorn unless the user asks.
- `COM_PORT` is **COM8** in `main.py`.
- For full workflow details, follow `.cursor/skills/stop-app/SKILL.md`.
