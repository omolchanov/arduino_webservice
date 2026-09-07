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
- After editing firmware under `arduino/`

## Sketch required

**Do not flash without an explicit sketch.** If the user runs `/flash-arduino` with no sketch, ask which one before continuing.

Known production sketches:

| Short name | Path |
|------------|------|
| `valves` | `arduino/valves/` |
| `simple01` | `arduino/simple01/` |
| `sensors` | `arduino/sensors/` |
| `mulie_function` | `arduino/mulie_function/` |
| `mux` | `arduino/mux/` |
| `demux` | `arduino/demux/` |

## Prerequisites

1. Run `/stop-app` first if uvicorn is running (the flash script also calls stop-app automatically).
2. Close **Arduino Serial Monitor** — it blocks COM8.
3. `arduino-cli` must be on PATH (`arduino:avr:uno` core installed).

## Steps

1. Confirm the sketch name or path with the user if not provided.
2. Run from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch <sketch>
```

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch mux
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch arduino/valves
```

3. Report success or the compile/upload error from `arduino-cli`.

## Optional port override

Default port is **COM8** (`main.py`). For a different board:

```powershell
powershell -ExecutionPolicy Bypass -File .cursor/skills/flash-arduino/scripts/flash-arduino.ps1 -Sketch mux -Port COM3
```

## Failure handling

- **Port busy**: run `/stop-app`, close Serial Monitor, retry once.
- **Compile error**: show `arduino-cli` output; fix the sketch before retrying upload.
- **Sketch not found**: list the known sketches table above.

## Notes

- Shared headers live in `arduino/*.h`; the script passes `-Iarduino` like `scripts/arduino_test.ps1`.
- Do not start uvicorn after flashing unless the user asks.
