#ifndef VALVE_LOGIC_H
#define VALVE_LOGIC_H

#include <Arduino.h>
#include <string.h>

inline bool evalGate(const char* gate, bool a, bool b) {
  if (strcmp(gate, "AND") == 0) {
    return a && b;
  }
  if (strcmp(gate, "OR") == 0) {
    return a || b;
  }
  if (strcmp(gate, "NOT") == 0) {
    return !a;
  }
  if (strcmp(gate, "NAND") == 0) {
    return !(a && b);
  }
  if (strcmp(gate, "NOR") == 0) {
    return !(a || b);
  }
  if (strcmp(gate, "XOR") == 0) {
    return a ^ b;
  }
  if (strcmp(gate, "XNOR") == 0) {
    return !(a ^ b);
  }
  return false;
}

#endif
