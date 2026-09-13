#ifndef TV_REMOTE_LOGIC_H
#define TV_REMOTE_LOGIC_H

#include <stddef.h>
#include <stdint.h>

struct RemoteCodeEntry {
  uint32_t code;
  const char* label;
};

static const RemoteCodeEntry REMOTE_CODE_TABLE[] = {
    {0xFFA25D, "POWER"},
    {0xFF629D, "CH+"},
    {0xFFE21D, "CH-"},
    {0xFF22DD, "VOL+"},
    {0xFF02FD, "VOL-"},
    {0xFFC23D, "MUTE"},
    {0xFFE01F, "INPUT"},
    {0xFF9867, "0"},
    {0xFFB04F, "1"},
    {0xFF30CF, "2"},
    {0xFF18E7, "3"},
    {0xFF7A85, "4"},
    {0xFF10EF, "5"},
    {0xFF38C7, "6"},
    {0xFF5AA5, "7"},
    {0xFF42BD, "8"},
    {0xFF4AB5, "9"},
};

static const size_t REMOTE_CODE_TABLE_LEN =
    sizeof(REMOTE_CODE_TABLE) / sizeof(REMOTE_CODE_TABLE[0]);

inline const char* remoteLabelForCode(uint32_t code) {
  for (size_t i = 0; i < REMOTE_CODE_TABLE_LEN; i++) {
    if (REMOTE_CODE_TABLE[i].code == code) {
      return REMOTE_CODE_TABLE[i].label;
    }
  }
  return nullptr;
}

#endif
