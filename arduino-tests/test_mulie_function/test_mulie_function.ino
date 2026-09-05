#include <AUnit.h>
#include "display_math.h"

using namespace aunit;

test(increment_digit_wraps) {
  byte d = 9;
  increment_digit(d);
  assertEqual((int)d, 0);
}

test(increment_digit_normal) {
  byte d = 5;
  increment_digit(d);
  assertEqual((int)d, 6);
}

test(rebuild_counter) {
  assertEqual(rebuild_counter(1, 0, 5), 105);
  assertEqual(rebuild_counter(9, 0, 0), 900);
}

test(clamp_counter) {
  assertEqual(clamp_counter(-1), 0);
  assertEqual(clamp_counter(1000), 999);
  assertEqual(clamp_counter(42), 42);
}

test(split_display_digits) {
  byte digits[4];
  split_display_digits(105, digits);
  assertEqual((int)digits[0], 0);
  assertEqual((int)digits[1], 1);
  assertEqual((int)digits[2], 0);
  assertEqual((int)digits[3], 5);
}

test(split_three_digit_display_boot) {
  byte digits[4];
  split_three_digit_display(0, digits);
  assertEqual((int)digits[0], 0);
  assertEqual((int)digits[1], 0);
  assertEqual((int)digits[2], 0);
  assertEqual((int)digits[3], 0);
}

test(split_three_digit_display_value) {
  byte digits[4];
  split_three_digit_display(42, digits);
  assertEqual((int)digits[0], 0);
  assertEqual((int)digits[1], 0);
  assertEqual((int)digits[2], 4);
  assertEqual((int)digits[3], 2);
}

test(increment_hundreds_from_five) {
  assertEqual(increment_hundreds(5), 105);
}

test(increment_hundreds_wraps_at_nine) {
  assertEqual(increment_hundreds(900), 0);
}

test(increment_tens_from_ten) {
  assertEqual(increment_tens(10), 20);
}

test(increment_tens_wraps) {
  assertEqual(increment_tens(90), 0);
}

test(increment_ones_from_seven) {
  assertEqual(increment_ones(7), 8);
}

test(increment_ones_wraps) {
  assertEqual(increment_ones(9), 0);
}

test(increment_ones_on_109) {
  assertEqual(increment_ones(109), 100);
}

test(reset_counter_value) {
  assertEqual(reset_counter(), 0);
}

test(clock_start_minutes_value) {
  assertEqual(clock_start_minutes(), 720);
}

test(tick_clock_minutes_normal) {
  assertEqual(tick_clock_minutes(720), 721);
}

test(tick_clock_minutes_wraps_at_midnight) {
  assertEqual(tick_clock_minutes(1439), 0);
}

test(minutes_to_hours_minutes_noon) {
  byte hours = 0;
  byte mins = 0;
  minutes_to_hours_minutes(720, hours, mins);
  assertEqual((int)hours, 12);
  assertEqual((int)mins, 0);
}

test(minutes_to_hours_minutes_midnight) {
  byte hours = 0;
  byte mins = 0;
  minutes_to_hours_minutes(0, hours, mins);
  assertEqual((int)hours, 0);
  assertEqual((int)mins, 0);
}

test(split_clock_display_noon) {
  byte digits[4];
  split_clock_display(12, 0, digits);
  assertEqual((int)digits[0], 1);
  assertEqual((int)digits[1], 2);
  assertEqual((int)digits[2], 0);
  assertEqual((int)digits[3], 0);
}

test(split_clock_display_leading_zero_hour) {
  byte digits[4];
  split_clock_display(9, 5, digits);
  assertEqual((int)digits[0], 0);
  assertEqual((int)digits[1], 9);
  assertEqual((int)digits[2], 0);
  assertEqual((int)digits[3], 5);
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
