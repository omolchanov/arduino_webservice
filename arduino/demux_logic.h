#ifndef DEMUX_LOGIC_H
#define DEMUX_LOGIC_H

inline bool demux_y0(bool a, bool di) {
  return !a && di;
}

inline bool demux_y1(bool a, bool di) {
  return a && di;
}

#endif
