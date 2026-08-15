## Why

The Arduino sketch now blinks an LED on D12 when a key is pressed and sends keys in a `Pressed: X` serial format with a startup banner. The webservice must accept this protocol so keys continue to appear in the browser.

## What Changes

- Update `arduino/keypad.ino` with LED on pin 12, blink on key press, and `Pressed: <key>` serial output
- Update `main.py` serial parser to extract keys from `Pressed: X` lines and ignore the `Keypad ready` banner
- Keep existing WebSocket broadcast and live UI behavior unchanged

## Capabilities

### Modified Capabilities

- `keypad-display`: serial message format and Arduino LED feedback on key press

## Impact

- **Arduino**: LED wired to D12; sketch sends `Pressed: 5` instead of `5`
- **Backend**: `read_keys()` parsing logic in `main.py`
- **Frontend**: no changes required (keys still arrive as `{"type": "key", "key": "5"}`)
- **Hardware note**: LED blink is physical on the board; web UI unchanged unless optional visual feedback is added later
