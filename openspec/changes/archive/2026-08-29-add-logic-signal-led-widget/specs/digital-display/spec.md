## ADDED Requirements

### Requirement: Logic signal LED widget

The Digital Signal dashboard SHALL include a logic signal LED widget that displays the live button-driven logic state on D8 as `0` or `1`, representing the `Signal:` field from `arduino/simple01.ino`. The widget SHALL be placed in the same row as the potentiometer, detected logic LED, current, and resistance widgets. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Logic signal widget updates on new reading

- **WHEN** the page receives a WebSocket `logic` event with `"value": 1`
- **THEN** the logic signal LED widget displays `1`

#### Scenario: Logic signal widget updates on LOW reading

- **WHEN** the page receives a WebSocket `logic` event with `"value": 0`
- **THEN** the logic signal LED widget displays `0`

#### Scenario: Logic signal widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_logic_value": 1`
- **THEN** the logic signal LED widget displays `1` before any new serial data arrives

### Requirement: Live value widgets row layout

The Digital Signal dashboard SHALL display exactly five live value widgets — potentiometer, detected logic LED, current, resistance, and logic signal LED — in a single horizontal row at the top of the dashboard grid.

#### Scenario: Five widgets appear in one row

- **WHEN** a user loads `/digital` on a desktop-width viewport
- **THEN** all five live value widgets are rendered side by side in one row above the history graphs

## MODIFIED Requirements

### Requirement: Logic signal graph widget

The Digital Signal dashboard SHALL include a logic signal graph widget titled **Logic signal LED history** that plots live 0/1 values over time as a stepped line chart with a rolling client-side history buffer. The graph card SHALL NOT include a separate large inline current-value display; the live value SHALL be shown only in the logic signal LED value widget.

#### Scenario: Graph updates on new logic value

- **WHEN** the page receives a WebSocket `logic` event with `"value": 1` or `"value": 0`
- **THEN** the logic signal LED history graph appends the new point

#### Scenario: Graph shows only 0 and 1 on Y-axis

- **WHEN** the logic signal LED history graph is rendered
- **THEN** the Y-axis displays only values 0 and 1

### Requirement: Resistance widget

The Digital Signal dashboard SHALL include a resistance widget that displays the live LED resistance reading formatted to one decimal place with a **Ω** unit label. The widget SHALL be placed in the same row as the potentiometer, detected logic LED, current, and logic signal LED widgets. The widget SHALL include a status dot that follows the same online/offline and pending-reading pattern as sensor widgets on the Sensors dashboard.

#### Scenario: Resistance widget updates on new reading

- **WHEN** the page receives a WebSocket `resistance` event with `"ohm": 162.6`
- **THEN** the resistance widget displays `162.6` with unit **Ω**

#### Scenario: Resistance widget seeds from status API

- **WHEN** a user loads `/digital` and `GET /api/status` returns `"last_led_resistance_ohm": 85.3`
- **THEN** the resistance widget displays `85.3` before any new serial data arrives
