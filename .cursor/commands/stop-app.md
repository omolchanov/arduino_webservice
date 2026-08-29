---
name: /stop-app
id: stop-app
category: Workflow
description: Stop the uvicorn server and release COM8
---

Stops the uvicorn server and release COM8

Read and follow `.cursor/skills/stop-app/SKILL.md`.

**Steps**

1. Run `.cursor/skills/stop-app/scripts/stop-app.ps1` from the project root.
2. Confirm no `uvicorn main:app` process is running.
3. Tell the user COM8 is released (or that no server was running).
