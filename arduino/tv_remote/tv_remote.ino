// TV Remote IR receiver — standalone sketch for Arduino IDE
// Wiring: IR receiver OUT -> D2, VCC -> 5V, GND -> GND
// Requires IRremote library: arduino-cli lib install "IRremote"

#include <IRremote.hpp>
#include "tv_remote_logic.h"

const uint8_t IR_PIN = 2;
const uint16_t DEBOUNCE_MS = 300;

uint32_t lastCode = 0;
unsigned long lastPressMs = 0;

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
  Serial.println("Remote ready");
}

void loop() {
  if (!IrReceiver.decode()) {
    return;
  }

  if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) {
    IrReceiver.resume();
    return;
  }

  uint32_t code = IrReceiver.decodedIRData.decodedRawData;
  unsigned long now = millis();
  if (code == lastCode && (now - lastPressMs) < DEBOUNCE_MS) {
    IrReceiver.resume();
    return;
  }
  lastCode = code;
  lastPressMs = now;

  const char* label = remoteLabelForCode(code);
  if (label) {
    Serial.print("Remote: ");
    Serial.println(label);
  } else {
    Serial.print("Remote: UNKNOWN (0x");
    Serial.print(code, HEX);
    Serial.println(")");
  }

  IrReceiver.resume();
}
