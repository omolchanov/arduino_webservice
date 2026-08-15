## MODIFIED Requirements

### Requirement: Serial key ingestion

The system SHALL read key characters from an Arduino Uno over USB serial at 9600 baud. Valid keys are digits `0`–`9`, symbols `*` and `#`, and letters `A`–`D`. The server SHALL accept key lines in either format:

- `Pressed: <key>` (preferred, from LED-enabled sketch)
- `<key>` alone on a line (legacy format)

Startup banner lines such as `Keypad ready` SHALL be ignored. Each valid key received SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "key", "key": "<char>"}`.

#### Scenario: Key received in Pressed format

- **WHEN** the Arduino sends `Pressed: 5\n` over serial
- **THEN** the server broadcasts `{"type": "key", "key": "5"}` to all connected WebSocket clients

#### Scenario: Legacy single-character format still works

- **WHEN** the Arduino sends `5\n` over serial
- **THEN** the server broadcasts `{"type": "key", "key": "5"}` to all connected WebSocket clients

#### Scenario: Startup banner ignored

- **WHEN** the Arduino sends `Keypad ready\n` on boot
- **THEN** the server ignores it and does not broadcast

#### Scenario: Invalid serial data ignored

- **WHEN** the serial port sends an empty line or a line that does not contain a valid key
- **THEN** the server ignores it and does not broadcast

### Requirement: Arduino LED feedback on key press

The Arduino sketch SHALL blink an LED connected to pin D12 for 100ms on each debounced key press. This is hardware-only feedback and does not require web UI changes.

#### Scenario: LED blinks on key press

- **WHEN** a valid key is pressed on the keypad
- **THEN** the Arduino sets D12 HIGH for 100ms then LOW
- **AND** sends `Pressed: <key>` over serial
