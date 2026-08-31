#ifndef MEASUREMENT_H
#define MEASUREMENT_H

#define LOGIC_THRESHOLD_LOW 1.5f
#define LOGIC_THRESHOLD_HIGH 3.0f

inline float adcToVolts(int adc) {
  return adc * 5.0f / 1023.0f;
}

inline float logicZone(float voltage) {
  if (voltage < LOGIC_THRESHOLD_LOW) {
    return 0.0f;
  }
  if (voltage < LOGIC_THRESHOLD_HIGH) {
    return 0.5f;
  }
  return 1.0f;
}

inline float currentMa(int shuntAdc, float shuntOhms) {
  float shuntVoltage = adcToVolts(shuntAdc);
  return (shuntVoltage / shuntOhms) * 1000.0f;
}

inline float ledResistance(float ledVoltage, float currentA) {
  if (currentA <= 0.0001f) {
    return 0.0f;
  }
  return ledVoltage / currentA;
}

#define POT_BRIGHTNESS_MIN_ADC 614
#define POT_BRIGHTNESS_MAX_ADC 1023

inline int brightnessForPot(int adc) {
  if (adc < POT_BRIGHTNESS_MIN_ADC) {
    return 0;
  }
  if (adc >= POT_BRIGHTNESS_MAX_ADC) {
    return 255;
  }
  return (adc - POT_BRIGHTNESS_MIN_ADC) * 255 /
         (POT_BRIGHTNESS_MAX_ADC - POT_BRIGHTNESS_MIN_ADC);
}

#endif
