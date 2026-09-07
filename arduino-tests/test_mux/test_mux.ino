#include <AUnit.h>
#include "mux_logic.h"

using namespace aunit;

test(mux_a0_di0_low_di1_low) {
  assertEqual(false, mux2to1(false, false, false));
}

test(mux_a0_di0_low_di1_high) {
  assertEqual(false, mux2to1(false, false, true));
}

test(mux_a0_di0_high_di1_low) {
  assertEqual(true, mux2to1(false, true, false));
}

test(mux_a0_di0_high_di1_high) {
  assertEqual(true, mux2to1(false, true, true));
}

test(mux_a1_di0_low_di1_low) {
  assertEqual(false, mux2to1(true, false, false));
}

test(mux_a1_di0_low_di1_high) {
  assertEqual(true, mux2to1(true, false, true));
}

test(mux_a1_di0_high_di1_low) {
  assertEqual(false, mux2to1(true, true, false));
}

test(mux_a1_di0_high_di1_high) {
  assertEqual(true, mux2to1(true, true, true));
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
