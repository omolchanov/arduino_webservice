#include <AUnit.h>
#include "demux_logic.h"

using namespace aunit;

test(demux_a0_di_low) {
  assertEqual(false, demux_y0(false, false));
  assertEqual(false, demux_y1(false, false));
}

test(demux_a0_di_high) {
  assertEqual(true, demux_y0(false, true));
  assertEqual(false, demux_y1(false, true));
}

test(demux_a1_di_low) {
  assertEqual(false, demux_y0(true, false));
  assertEqual(false, demux_y1(true, false));
}

test(demux_a1_di_high) {
  assertEqual(false, demux_y0(true, true));
  assertEqual(true, demux_y1(true, true));
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
