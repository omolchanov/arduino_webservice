#ifndef SENSOR_MATH_H
#define SENSOR_MATH_H

inline float distanceCm(long duration) {
  return duration * 0.0343f / 2.0f;
}

inline int invertLight(int adc) {
  return 1023 - adc;
}

inline float tempC(int lm35Adc) {
  float voltage = lm35Adc * 5.0f / 1023.0f;
  return voltage * 100.0f / 2.0f;
}

#endif
