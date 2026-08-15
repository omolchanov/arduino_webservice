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

## OpenSpec workflow

1. `/opsx:propose <change-name>` — create proposal, design, tasks, specs
2. `/opsx:apply <change-name>` — implement on `feature-<change-name>` branch
3. `/opsx:archive <change-name>` — sync specs, commit, push, archive change

## Conventions

- Keep Python code minimal and focused
- No MVC folders unless a change explicitly requires it
- COM port configured as constant in `main.py` (`COM8`)
- Close Arduino Serial Monitor before starting the Python app
