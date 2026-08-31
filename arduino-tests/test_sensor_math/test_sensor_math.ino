#include <AUnit.h>
#include "sensor_math.h"

using namespace aunit;

test(distance_cm) {
  assertNear(9.947f, distanceCm(580), 0.01f);
}

test(invert_light) {
  assertEqual((int)1023, invertLight(0));
  assertEqual((int)0, invertLight(1023));
  assertEqual((int)512, invertLight(511));
}

test(temp_c) {
  assertNear(25.0f, tempC(102), 0.5f);
}

void setup() {
  Serial.begin(9600);
  delay(2000);
}

void loop() {
  TestRunner::run();
}
