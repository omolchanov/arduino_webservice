#include "condensator_logic.h"

const int chargePin = 8;
const int dischargePin = 9;
const int sensorPin = A0;

const int sampleDelay = 1000;
const int numSamples = 10;

void setup() {
  Serial.begin(9600);
  pinMode(chargePin, OUTPUT);
  pinMode(dischargePin, OUTPUT);
  digitalWrite(chargePin, LOW);
  digitalWrite(dischargePin, LOW);
}

void loop() {
  pinMode(dischargePin, INPUT);
  digitalWrite(chargePin, HIGH);

  Serial.println("Charging...");
  for (int i = 0; i < numSamples; i++) {
    float voltage = voltageFromAdc(analogRead(sensorPin));
    float chargeC = chargeMicroCoulombs(voltage, CONDENSATOR_CAPACITANCE_F);

    Serial.print("V = ");
    Serial.print(voltage);
    Serial.print(" V   Q = ");
    Serial.print(chargeC);
    Serial.println(" uC");

    delay(sampleDelay);
  }

  pinMode(chargePin, INPUT);
  pinMode(dischargePin, OUTPUT);
  digitalWrite(dischargePin, LOW);

  Serial.println("Discharging...");
  for (int i = 0; i < numSamples; i++) {
    float voltage = voltageFromAdc(analogRead(sensorPin));
    float chargeC = chargeMicroCoulombs(voltage, CONDENSATOR_CAPACITANCE_F);

    Serial.print("V = ");
    Serial.print(voltage);
    Serial.print(" V   Q = ");
    Serial.print(chargeC);
    Serial.println(" uC");

    delay(sampleDelay);
  }
}
