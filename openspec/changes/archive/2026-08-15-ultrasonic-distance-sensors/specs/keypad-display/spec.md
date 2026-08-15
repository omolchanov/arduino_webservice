## ADDED Requirements

### Requirement: Serial key ingestion

The serial read loop SHALL parse both keypad key lines and `Distance: <number> cm` lines from the same COM port connection, broadcasting the appropriate WebSocket event type for each.

## MODIFIED Requirements

_None — distance parsing is additive; existing key scenarios unchanged._
