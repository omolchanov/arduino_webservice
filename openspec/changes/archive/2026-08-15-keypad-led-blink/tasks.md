## 1. Arduino sketch

- [x] 1.1 Update `arduino/keypad.ino` with LED on D12, blink on press, `Pressed: <key>` output, and `Keypad ready` banner

## 2. Backend parser

- [x] 2.1 Add `parse_key_line()` to extract key from `Pressed: X` or legacy single-char lines
- [x] 2.2 Update `read_keys()` to use parser and ignore `Keypad ready`
- [x] 2.3 Ignore invalid lines without breaking the serial read loop

## 3. Verification

- [x] 3.1 Upload sketch, start server, press keys — verify keys appear in browser
- [x] 3.2 Confirm `Keypad ready` does not appear as a key in the UI
