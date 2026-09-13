# tv-remote-display Specification

## Purpose

Decode infrared TV remote button presses on Arduino Uno and display the labeled key live in a browser on a TV Remote dashboard, following the project's one-sketch-per-page serial pattern.

## Requirements

### Requirement: One sketch per TV Remote dashboard

The TV Remote dashboard SHALL be driven exclusively by the dedicated firmware at `arduino/tv_remote/tv_remote.ino`. The system SHALL NOT require or support combining this dashboard with keypad, sensors, valves, mux, demux, or other production sketches in a single firmware upload.

#### Scenario: User runs TV Remote dashboard

- **WHEN** the user wants to view the TV Remote dashboard at `/tv-remote`
- **THEN** the user uploads `arduino/tv_remote/tv_remote.ino` to the Arduino (not `keypad`, `sensors.ino`, or other production sketches)

### Requirement: IR remote serial ingestion

The system SHALL read IR remote key lines from `arduino/tv_remote/tv_remote.ino` over USB serial at 9600 baud. Lines matching `Remote: <label>` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "remote", "key": "<label>", "code": null}`. Lines matching `Remote: UNKNOWN (0x<hex>)` SHALL broadcast `{"type": "remote", "key": "UNKNOWN", "code": <integer>}`. Startup banner lines such as `Remote ready` SHALL be ignored.

#### Scenario: Known button received

- **WHEN** the Arduino sends `Remote: POWER\n` over serial
- **THEN** the server broadcasts `{"type": "remote", "key": "POWER", "code": null}` to all connected WebSocket clients

#### Scenario: Unknown code received

- **WHEN** the Arduino sends `Remote: UNKNOWN (0xFF629D)\n` over serial
- **THEN** the server broadcasts `{"type": "remote", "key": "UNKNOWN", "code": 16755101}` (decimal equivalent of `0xFF629D`) to all connected WebSocket clients

#### Scenario: Startup banner ignored

- **WHEN** the Arduino sends `Remote ready\n` on boot
- **THEN** the server ignores it and does not broadcast

#### Scenario: Invalid remote line ignored

- **WHEN** the serial port sends a line that does not match the remote format
- **THEN** the server does not broadcast a remote event (may still parse as keypad, sensor, or other applicable formats)

### Requirement: Remote values in status API

`GET /api/status` SHALL include `last_remote_key` as a string or `null`, and `last_remote_code` as an integer or `null`, when no reading has been received both fields SHALL be `null`.

#### Scenario: Status includes last remote key

- **WHEN** a client requests `GET /api/status` after `Remote: VOL+\n` has been parsed
- **THEN** the response includes `"last_remote_key": "VOL+"` and `"last_remote_code": null`

#### Scenario: Status includes unknown code

- **WHEN** a client requests `GET /api/status` after `Remote: UNKNOWN (0xFF629D)\n` has been parsed
- **THEN** the response includes `"last_remote_key": "UNKNOWN"` and `"last_remote_code": 16755101`

### Requirement: TV Remote dashboard page

The system SHALL serve a TV Remote dashboard at `GET /tv-remote` from `static/tv_remote.html`. The page SHALL reuse the same visual patterns as the Keypad and other dashboards (sidebar navigation, dark theme, card layout, online/offline status badge in the top-right, custom toast notifications — no browser `alert()`).

#### Scenario: TV Remote page loads

- **WHEN** a user navigates to `/tv-remote`
- **THEN** the browser displays the TV Remote dashboard with sidebar navigation including links to Keypad, Sensors, Digital Signal, Valves, Display, Multiplexor, Demultiplexor, and TV Remote

### Requirement: Last button widget

The TV Remote dashboard SHALL display the most recently received remote label prominently in a **Last Button** card. When no remote event has been received yet, the widget SHALL show a placeholder (e.g. em dash).

#### Scenario: Last button updates on remote event

- **WHEN** the page receives a WebSocket `remote` event with `"key": "CH+"`
- **THEN** the Last Button widget displays `CH+`

### Requirement: Recent buttons history

The TV Remote dashboard SHALL maintain a scrolling list of recent remote labels (newest first), capped at 50 entries. Each new `remote` WebSocket event SHALL prepend its label to the list.

#### Scenario: History appends on press

- **WHEN** the page receives WebSocket `remote` events for `POWER` then `1`
- **THEN** the Recent Buttons list shows `1` above `POWER` at the top

### Requirement: Raw code display for unknown keys

When a `remote` WebSocket event includes a non-null `code`, the TV Remote dashboard SHALL show the hexadecimal code (e.g. `0xFF629D`) alongside or below the Last Button label.

#### Scenario: Unknown code shown

- **WHEN** the page receives `{"type": "remote", "key": "UNKNOWN", "code": 16755101}`
- **THEN** the page displays `UNKNOWN` and a raw code of `0xFF629D`

### Requirement: WebSocket cached remote state on connect

When a WebSocket client connects to `/ws`, if a remote key has previously been parsed, the server SHALL send a cached `{"type": "remote", "key": "<label>", "code": <int|null>, "cached": true}` message before live events.

#### Scenario: Cached remote on reconnect

- **WHEN** a client connects to `/ws` after `Remote: MUTE\n` was already parsed
- **THEN** the client receives a message with `"type": "remote"`, `"key": "MUTE"`, and `"cached": true`

### Requirement: TV Remote navigation link

All existing dashboard pages SHALL include a **TV Remote** link in the sidebar pointing to `/tv-remote`.

#### Scenario: Nav link on Keypad page

- **WHEN** a user views the Keypad page at `/`
- **THEN** the sidebar includes a link labeled TV Remote to `/tv-remote`
