#include <AUnit.h>
#include "condensator_logic.h"

using namespace aunit;

test(voltage_from_adc) {
  assertNear(0.0f, voltageFromAdc(0), 0.001f);
  assertNear(CONDENSATOR_VCC, voltageFromAdc(CONDENSATOR_ADC_MAX), 0.01f);
  assertNear(2.44f, voltageFromAdc(500), 0.02f);
}

test(charge_micro_coulombs) {
  assertNear(0.0f, chargeMicroCoulombs(0.0f, CONDENSATOR_CAPACITANCE_F), 0.001f);
  assertNear(
    1100.0f,
    chargeMicroCoulombs(CONDENSATOR_VCC, CONDENSATOR_CAPACITANCE_F),
    0.1f
  );
  assertNear(539.0f, chargeMicroCoulombs(2.45f, CONDENSATOR_CAPACITANCE_F), 0.1f);
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
