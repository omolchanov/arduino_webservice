#ifndef VALVE_LOGIC_H
#define VALVE_LOGIC_H

#include <Arduino.h>
#include <string.h>

inline bool isValidGateCommand(const char* cmd) {
  return strcmp(cmd, "AND") == 0 ||
         strcmp(cmd, "OR") == 0 ||
         strcmp(cmd, "NOT") == 0 ||
         strcmp(cmd, "NAND") == 0 ||
         strcmp(cmd, "NOR") == 0 ||
         strcmp(cmd, "XOR") == 0 ||
         strcmp(cmd, "XNOR") == 0;
}

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
