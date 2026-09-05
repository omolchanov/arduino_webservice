#ifndef DISPLAY_MATH_H
#define DISPLAY_MATH_H

#include <Arduino.h>

inline void increment_digit(byte &d) {
  d = (d + 1) % 10;
}

inline int rebuild_counter(byte h, byte t, byte o) {
  if (h > 9) {
    h = 9;
  }
  if (t > 9) {
    t = 9;
  }
  if (o > 9) {
    o = 9;
  }
  return h * 100 + t * 10 + o;
}

inline int clamp_counter(int value) {
  if (value < 0) {
    return 0;
  }
  if (value > 999) {
    return 999;
  }
  return value;
}

inline int increment_hundreds(int counter) {
  byte h = counter / 100;
  byte t = (counter / 10) % 10;
  byte o = counter % 10;
  increment_digit(h);
  return clamp_counter(rebuild_counter(h, t, o));
}

inline int increment_tens(int counter) {
  byte h = counter / 100;
  byte t = (counter / 10) % 10;
  byte o = counter % 10;
  increment_digit(t);
  return clamp_counter(rebuild_counter(h, t, o));
}

inline int increment_ones(int counter) {
  byte h = counter / 100;
  byte t = (counter / 10) % 10;
  byte o = counter % 10;
  increment_digit(o);
  return clamp_counter(rebuild_counter(h, t, o));
}

inline int reset_counter() {
  return 0;
}

inline void split_three_digit_display(int number, byte digits[4]) {
  number = clamp_counter(number);
  digits[0] = 0;
  digits[1] = number / 100;
  digits[2] = (number / 10) % 10;
  digits[3] = number % 10;
}

inline void split_display_digits(int number, byte digits[4]) {
  if (number < 0) {
    number = 0;
  }
  if (number > 9999) {
    number = 9999;
  }
  digits[0] = number / 1000;
  digits[1] = (number / 100) % 10;
  digits[2] = (number / 10) % 10;
  digits[3] = number % 10;
}

inline int clock_start_minutes() {
  return 720;
}

inline int tick_clock_minutes(int minutes) {
  return (minutes + 1) % 1440;
}

inline void minutes_to_hours_minutes(int totalMinutes, byte &hours, byte &mins) {
  totalMinutes = totalMinutes % 1440;
  if (totalMinutes < 0) {
    totalMinutes += 1440;
  }
  hours = totalMinutes / 60;
  mins = totalMinutes % 60;
}

inline void split_clock_display(byte hours, byte minutes, byte digits[4]) {
  digits[0] = hours / 10;
  digits[1] = hours % 10;
  digits[2] = minutes / 10;
  digits[3] = minutes % 10;
}

#endif
