#ifndef CONDENSATOR_LOGIC_H
#define CONDENSATOR_LOGIC_H

#define CONDENSATOR_VCC 5.0f
#define CONDENSATOR_CAPACITANCE_F 220e-6f
#define CONDENSATOR_ADC_MAX 1023

inline float voltageFromAdc(int adc, float vcc = CONDENSATOR_VCC) {
  return adc * (vcc / (float)CONDENSATOR_ADC_MAX);
}

inline float chargeMicroCoulombs(float voltage, float capacitanceFarads) {
  return voltage * capacitanceFarads * 1e6f;
}

#endif
