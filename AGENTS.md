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

Arduino firmware logic (AUnit + arduino-cli):

```bash
arduino-cli core install arduino:avr
arduino-cli lib install "AUnit"
powershell -File scripts/arduino_test.ps1 -CompileOnly
powershell -File scripts/arduino_test.ps1 -Port COM8
```

Arduino AUnit on Wokwi (simulated Uno, no board; requires internet):

```powershell
# Install Wokwi CLI: iwr https://wokwi.com/ci/install.ps1 -useb | iex
# Token: https://wokwi.com/dashboard/ci — set WOKWI_CLI_TOKEN (never commit)
$env:WOKWI_CLI_TOKEN = "your-token"
powershell -File scripts/wokwi_test.ps1
```

EpoxyDuino native AUnit (host, offline; clone EpoxyDuino + AUnit one level above repo):

```bash
make -C arduino-tests runtests
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
- `pytest/` — Python API tests; `arduino-tests/` — Arduino AUnit tests
- Production sketches: `arduino/valves/`, `arduino/simple01/`, `arduino/sensors/`
