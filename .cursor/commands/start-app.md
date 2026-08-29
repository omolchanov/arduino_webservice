---
name: /start-app
id: start-app
category: Workflow
description: Start the uvicorn server and connect COM8
---

Starts the uvicorn server and connects COM8

Read and follow `.cursor/skills/start-app/SKILL.md`.

**Steps**

1. If uvicorn is already running, report http://127.0.0.1:8000 and stop.
2. Otherwise run `.cursor/skills/start-app/scripts/start-app.ps1` or `uvicorn main:app --reload` in a background shell.
3. Confirm the server responds and report COM8 status.
