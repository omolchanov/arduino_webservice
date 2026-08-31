#include "measurement.h"

#define SIGNAL_PIN 8
#define POT_PIN A0
#define LED_PIN 9
#define CURRENT_PIN A1
#define LED_VOLTAGE_PIN A2
#define BUTTON_PIN 2

#define SHUNT_RESISTOR 10.0

bool signalState = false;
bool undefinedLedState = false;

bool lastButtonReading = HIGH;
bool buttonState = HIGH;

unsigned long lastDebounceTime = 0;
unsigned long lastMeasurementTime = 0;

const unsigned long debounceDelay = 50;
const unsigned long measurementInterval = 1000;

void setup() {
  pinMode(SIGNAL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.begin(9600);

  digitalWrite(SIGNAL_PIN, LOW);
}

void loop() {

  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {

    if (reading != buttonState) {

      buttonState = reading;

      if (buttonState == LOW) {

        signalState = !signalState;

        digitalWrite(SIGNAL_PIN, signalState);
      }
    }
  }

  lastButtonReading = reading;

  if (millis() - lastMeasurementTime >= measurementInterval) {

    lastMeasurementTime = millis();

    int analogValue = analogRead(POT_PIN);

    float voltage = adcToVolts(analogValue);

    String logicState;

    int brightness = 0;

    float zone = logicZone(voltage);

    if (zone == 0.0f) {

      logicState = "0 (LOW)";

      analogWrite(LED_PIN, 0);

    }

    else if (zone == 0.5f) {

      logicState = "UNDEFINED";

      undefinedLedState = !undefinedLedState;

      if (undefinedLedState) {
        digitalWrite(LED_PIN, HIGH);
      }
      else {
        digitalWrite(LED_PIN, LOW);
      }

    }

    else {

      logicState = "1 (HIGH)";

      brightness = brightnessForPot(analogValue);

      analogWrite(LED_PIN, brightness);
    }

    int currentADC = analogRead(CURRENT_PIN);

    float shuntVoltage = adcToVolts(currentADC);

    float current = shuntVoltage / SHUNT_RESISTOR;

    float current_mA = currentMa(currentADC, SHUNT_RESISTOR);

    int ledVoltageADC = analogRead(LED_VOLTAGE_PIN);

    float d9Voltage = adcToVolts(ledVoltageADC);

    float ledVoltage = d9Voltage - shuntVoltage;

    if (ledVoltage < 0) {
      ledVoltage = 0;
    }

    float ledResistanceValue = ledResistance(ledVoltage, current);

    Serial.print("Signal: ");
    Serial.print(signalState ? "1" : "0");

    Serial.print(" | Pot: ");
    Serial.print(voltage, 2);
    Serial.print(" V");

    Serial.print(" | Logic: ");
    Serial.print(logicState);

    Serial.print(" | Shunt: ");
    Serial.print(shuntVoltage, 3);
    Serial.print(" V");

    Serial.print(" | Current: ");
    Serial.print(current_mA, 1);
    Serial.print(" mA");

    Serial.print(" | LED Resistance: ");
    Serial.print(ledResistanceValue, 1);
    Serial.println(" Ohm");
  }
}
