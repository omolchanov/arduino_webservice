#include <AUnit.h>
#include "valve_logic.h"

using namespace aunit;

test(and_gate) {
  assertFalse(evalGate("AND", 0, 0));
  assertFalse(evalGate("AND", 0, 1));
  assertFalse(evalGate("AND", 1, 0));
  assertTrue(evalGate("AND", 1, 1));
}

test(or_gate) {
  assertFalse(evalGate("OR", 0, 0));
  assertTrue(evalGate("OR", 0, 1));
  assertTrue(evalGate("OR", 1, 0));
  assertTrue(evalGate("OR", 1, 1));
}

test(not_gate) {
  assertTrue(evalGate("NOT", 0, 0));
  assertTrue(evalGate("NOT", 0, 1));
  assertFalse(evalGate("NOT", 1, 0));
  assertFalse(evalGate("NOT", 1, 1));
}

test(nand_gate) {
  assertTrue(evalGate("NAND", 0, 0));
  assertTrue(evalGate("NAND", 0, 1));
  assertTrue(evalGate("NAND", 1, 0));
  assertFalse(evalGate("NAND", 1, 1));
}

test(nor_gate) {
  assertTrue(evalGate("NOR", 0, 0));
  assertFalse(evalGate("NOR", 0, 1));
  assertFalse(evalGate("NOR", 1, 0));
  assertFalse(evalGate("NOR", 1, 1));
}

test(xor_gate) {
  assertFalse(evalGate("XOR", 0, 0));
  assertTrue(evalGate("XOR", 0, 1));
  assertTrue(evalGate("XOR", 1, 0));
  assertFalse(evalGate("XOR", 1, 1));
}

test(xnor_gate) {
  assertTrue(evalGate("XNOR", 0, 0));
  assertFalse(evalGate("XNOR", 0, 1));
  assertFalse(evalGate("XNOR", 1, 0));
  assertTrue(evalGate("XNOR", 1, 1));
}

test(valid_gate_commands) {
  assertTrue(isValidGateCommand("AND"));
  assertTrue(isValidGateCommand("OR"));
  assertTrue(isValidGateCommand("NOT"));
  assertTrue(isValidGateCommand("NAND"));
  assertTrue(isValidGateCommand("NOR"));
  assertTrue(isValidGateCommand("XOR"));
  assertTrue(isValidGateCommand("XNOR"));
}

test(invalid_gate_commands) {
  assertFalse(isValidGateCommand("FOO"));
  assertFalse(isValidGateCommand(""));
  assertFalse(isValidGateCommand("and"));
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
