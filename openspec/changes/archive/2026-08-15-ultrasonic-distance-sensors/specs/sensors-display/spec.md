## ADDED Requirements

### Requirement: Ultrasonic distance serial ingestion

The system SHALL read distance measurements from an Arduino Uno over USB serial at 9600 baud. Lines in the format `Distance: <number> cm` SHALL be parsed and broadcast to all connected WebSocket clients as JSON `{"type": "distance", "cm": <number>}`.

#### Scenario: Distance line received

- **WHEN** the Arduino sends `Distance: 42.50 cm\n` over serial
- **THEN** the server broadcasts `{"type": "distance", "cm": 42.5}` to all connected WebSocket clients

#### Scenario: Invalid distance line ignored

- **WHEN** the serial port sends a line that does not match the distance format
- **THEN** the server does not broadcast a distance event (may still parse as keypad if applicable)

### Requirement: Sensors page

The system SHALL serve a web page at `GET /sensors` that displays live distance readings from the Arduino. The page SHALL include a **Distance** section showing the latest value in centimeters and a Connected/Disconnected status label.

#### Scenario: Distance updates on Sensors page

- **WHEN** a WebSocket client on `/sensors` receives a distance broadcast
- **THEN** the Distance section updates to show the new value in cm

#### Scenario: Navigation between pages

- **WHEN** a user opens `/` or `/sensors`
- **THEN** both pages show navigation links to switch between Keypad and Sensors

## MODIFIED Requirements

### Requirement: Serial key ingestion

The system SHALL continue to read keypad key characters from serial in addition to distance lines. Key and distance parsing SHALL coexist in the same serial read loop without interfering with each other.

#### Scenario: Key and distance on separate uploads

- **WHEN** the keypad sketch is uploaded, key lines are broadcast as keys
- **WHEN** the distance sketch is uploaded, distance lines are broadcast as distance events
- **AND** the server handles either format on the same COM port connection
