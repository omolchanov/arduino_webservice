---
name: flash-arduino
description: >-
  Compiles and uploads an Arduino Uno sketch to COM8 via arduino-cli. Use when
  the user runs /flash-arduino, asks to flash or upload a sketch, or program the
  Arduino. A sketch name or path is mandatory — do not upload without one.
disable-model-invocation: true
---

# Flash Arduino

Flashes **Arduino Uno** on **COM8** using `arduino-cli`. **A sketch is mandatory.**

## When to use

- User runs `/flash-arduino <sketch>`
- User asks to upload, flash, or program the Arduino
- After editing a production sketch and the user wants it on hardware

## Mandatory sketch

**Do not flash without an explicit sketch.** If the user runs `/flash-arduino` with no sketch, ask which one before continuing.

Accept sketch as:

- Short name: `mux`, `demux`, `valves`, `simple01`, `sensors`, `mulie_function`
- Folder path: `arduino/mux`, `arduino/valves`
- Test project: `arduino-tests/test_mux` (only if the user asks for a test sketch)

Production sketches live under `arduino/<name>/`.

## Preconditions

1. Run `/stop-app` first if uvicorn is running (COM8 is shared with the FastAPI app).
2. Close **Arduino Serial Monitor** and any other app using COM8.
3. `arduino-cli` must be on PATH (`arduino:avr:uno` core installed).

## Steps

1. Resolve the sketch from the user's argument (see **Mandatory sketch**).
2. From the **project root**, run:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch <sketch>
```

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch mux
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch arduino/valves
```

3. Report success or the compile/upload error from `arduino-cli`.
4. Remind the user to open Serial Monitor at **9600 baud** if the sketch uses `Serial`.

## Defaults

| Setting | Value |
|---------|-------|
| Board | `arduino:avr:uno` |
| Port | `COM8` |
| Include path | `-Iarduino/` (for shared headers like `mux_logic.h`, `measurement.h`) |

Override port only if the user names a different COM port:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch mux -Port COM3
```

## Failure handling

- **Sketch missing**: list known production sketches and ask the user to pick one.
- **Port busy**: suggest `/stop-app`, close Serial Monitor, retry once.
- **Compile error**: show `arduino-cli` output; fix the sketch before retrying upload.

## Notes

- `COM8` matches `main.py` and `AGENTS.md`.
- Do not start uvicorn after flashing unless the user asks.
