#include <AUnit.h>
#include "sensor_math.h"

using namespace aunit;

test(distance_cm) {
  assertNear(9.947f, distanceCm(580), 0.01f);
  assertNear(0.0f, distanceCm(0), 0.001f);
  assertNear(17.15f, distanceCm(1000), 0.01f);
}

test(invert_light) {
  assertEqual((int)1023, invertLight(0));
  assertEqual((int)0, invertLight(1023));
  assertEqual((int)512, invertLight(511));
  assertEqual((int)256, invertLight(767));
}

test(temp_c) {
  assertNear(25.0f, tempC(102), 0.5f);
  assertNear(0.0f, tempC(0), 0.5f);
  assertNear(50.0f, tempC(205), 0.5f);
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
  TestRunner::setVerbosity(Verbosity::kDefault);
}

void loop() {
  TestRunner::run();
}
