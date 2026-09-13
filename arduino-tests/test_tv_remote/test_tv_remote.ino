#include <AUnit.h>
#include "tv_remote_logic.h"

using namespace aunit;

test(remote_power_code) {
  assertEqual("POWER", remoteLabelForCode(0xFFA25D));
}

test(remote_digit_codes) {
  assertEqual("0", remoteLabelForCode(0xFF9867));
  assertEqual("5", remoteLabelForCode(0xFF10EF));
  assertEqual("9", remoteLabelForCode(0xFF4AB5));
}

test(remote_volume_codes) {
  assertEqual("VOL+", remoteLabelForCode(0xFF22DD));
  assertEqual("VOL-", remoteLabelForCode(0xFF02FD));
}

test(remote_unknown_code) {
  assertNull(remoteLabelForCode(0xDEADBEEF));
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
