#ifndef MUX_LOGIC_H
#define MUX_LOGIC_H

inline bool mux2to1(bool a, bool di0, bool di1) {
  return a ? di1 : di0;
}

#endif
