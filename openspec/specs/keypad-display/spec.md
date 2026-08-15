# keypad-display Specification

## Purpose

Read 4x4 keypad input from an Arduino Uno over USB serial and display pressed keys live in a browser via WebSocket.

## Requirements

### Requirement: Serial key ingestion

The system SHALL read key characters from an Arduino Uno over USB serial at 9600 baud. Valid keys are digits `0`–`9`, symbols `*` and `#`, and letters `A`–`D`. Each valid key received SHALL be broadcast to all connected WebSocket clients as JSON `{"type": "key", "key": "<char>"}`.

#### Scenario: Key received from Arduino

- **WHEN** the Arduino sends a single character followed by a newline over serial (e.g. `5\n`)
- **THEN** the server broadcasts `{"type": "key", "key": "5"}` to all connected WebSocket clients

#### Scenario: Invalid serial data ignored

- **WHEN** the serial port sends an empty line or a character outside the valid key set
- **THEN** the server ignores it and does not broadcast

#### Scenario: Serial port unavailable

- **WHEN** the configured COM port cannot be opened at startup
- **THEN** the server still starts and serves the web page
- **AND** WebSocket connections remain available (no keys are broadcast until serial connects)

### Requirement: Serial auto-reconnect

The system SHALL automatically retry opening the serial port when the connection is lost and resume reading keys when the Arduino is reconnected.

#### Scenario: Arduino unplugged

- **WHEN** the serial connection is lost
- **THEN** the server marks status as disconnected
- **AND** retries opening the port periodically

#### Scenario: Arduino replugged

- **WHEN** the Arduino becomes available again on the configured COM port
- **THEN** the server reconnects automatically
- **AND** broadcasts a serial status update to WebSocket clients

### Requirement: Live keypad display

The system SHALL serve a web page at `GET /` that connects to a WebSocket and displays pressed keys in real time. The page SHALL show the most recently pressed key prominently and a scrolling list of recent keys.

#### Scenario: Key appears in browser

- **WHEN** a WebSocket client is connected and the server broadcasts a key
- **THEN** the page updates the last-key display and appends the key to the history list

#### Scenario: WebSocket reconnect

- **WHEN** the WebSocket connection drops
- **THEN** the page attempts to reconnect automatically
- **AND** shows a single connection status label (Connected / Disconnected)

### Requirement: Minimal project structure

The application SHALL use a single Python file (`main.py`) and a single HTML file (`static/index.html`) with embedded CSS and JavaScript. No MVC folder structure, database, or authentication for v1.

#### Scenario: Application starts

- **WHEN** the user runs `uvicorn main:app`
- **THEN** the server listens on the default port and serves the keypad display page at `/`
