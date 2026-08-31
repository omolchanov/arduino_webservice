#include <AUnitVerbose.h>
#include "measurement.h"

using namespace aunit;

test(adc_to_volts) {
  assertNear(0.0f, adcToVolts(0), 0.001f);
  assertNear(5.0f, adcToVolts(1023), 0.01f);
}

test(logic_zone) {
  assertNear(0.0f, logicZone(1.49f), 0.001f);
  assertNear(0.5f, logicZone(1.50f), 0.001f);
  assertNear(0.5f, logicZone(2.99f), 0.001f);
  assertNear(1.0f, logicZone(3.00f), 0.001f);
}

test(current_ma) {
  assertNear(20.0f, currentMa(41, 10.0f), 0.5f);
}

test(led_resistance) {
  assertNear(100.0f, ledResistance(1.0f, 0.01f), 1.0f);
  assertNear(0.0f, ledResistance(1.0f, 0.0f), 0.001f);
}

void setup() {
#if !defined(EPOXY_DUINO)
  delay(2000);
#endif
  Serial.begin(9600);
#if !defined(EPOXY_DUINO)
  while (!Serial);
#endif
#if defined(EPOXY_DUINO)
  Serial.setLineModeUnix();
#endif
  TestRunner::setVerbosity(Verbosity::kAll);
}

void loop() {
  TestRunner::run();
}
