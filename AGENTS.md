# Arduino Keypad Project

## Stack

- Python 3.12, FastAPI, uvicorn, pyserial
- Arduino Uno 4x4 matrix keypad (serial 9600 baud)
- Minimal layout: `main.py` + `static/index.html`

## Commands

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Tests

```bash
python -m pytest pytest/
```

### Arduino unit tests (EpoxyDuino, offline)

Clone [EpoxyDuino](https://github.com/bxparks/EpoxyDuino) and [AUnit](https://github.com/bxparks/AUnit) one level above the repo, then:

```bash
make -C arduino-tests runtests
```

| Sketch | Test project |
|--------|--------------|
| `arduino/valves/` | `arduino-tests/test_valves/` |
| `arduino/simple01/` | `arduino-tests/test_simple01/` |
| `arduino/sensors/` | `arduino-tests/test_sensors/` |

### Arduino compile and optional hardware tests

```bash
arduino-cli core install arduino:avr
arduino-cli lib install "AUnit"
powershell -File scripts/arduino_test.ps1 -CompileOnly
powershell -File scripts/arduino_test.ps1 -Port COM8
```

Close Arduino Serial Monitor before running tests or starting uvicorn.

## OpenSpec workflow

1. `/opsx:propose <change-name>` — create proposal, design, tasks, specs
2. `/opsx:apply <change-name>` — implement on `feature-<change-name>` branch
3. `/opsx:archive <change-name>` — sync specs, commit, push, archive change

## Conventions

- Keep Python code minimal and focused
- No MVC folders unless a change explicitly requires it
- COM port configured as constant in `main.py` (`COM8`)
- Close Arduino Serial Monitor before starting the Python app
- `pytest/` — Python API tests; `arduino-tests/` — Arduino AUnit unit tests
- Production sketches: `arduino/valves/`, `arduino/simple01/`, `arduino/sensors/`
