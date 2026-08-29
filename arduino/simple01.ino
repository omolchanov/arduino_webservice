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

  // ==========================================
  // 1. Обрабатываем кнопку постоянно
  // ==========================================

  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {

    if (reading != buttonState) {

      buttonState = reading;

      // Кнопка нажата
      if (buttonState == LOW) {

        signalState = !signalState;

        digitalWrite(SIGNAL_PIN, signalState);
      }
    }
  }

  lastButtonReading = reading;


  // ==========================================
  // 2. Измерения раз в секунду
  // ==========================================

  if (millis() - lastMeasurementTime >= measurementInterval) {

    lastMeasurementTime = millis();


    // ========================================
    // Считываем потенциометр
    // ========================================

    int analogValue = analogRead(POT_PIN);

    float voltage = analogValue * 5.0 / 1023.0;


    // ========================================
    // Определяем логическую зону
    // ========================================

    String logicState;

    int brightness = 0;

    if (voltage < 1.5) {

      // LOW
      logicState = "0 (LOW)";

      analogWrite(LED_PIN, 0);

    }

    else if (voltage < 3.0) {

      // UNDEFINED
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

      // HIGH
      logicState = "1 (HIGH)";

      brightness = map(
        analogValue,
        614,
        1023,
        0,
        255
      );

      analogWrite(LED_PIN, brightness);
    }


    // ========================================
    // Измеряем ток
    // ========================================

    int currentADC = analogRead(CURRENT_PIN);

    float shuntVoltage = currentADC * 5.0 / 1023.0;

    float current = shuntVoltage / SHUNT_RESISTOR;

    float current_mA = current * 1000.0;


    // ========================================
    // Измеряем напряжение на LED
    // ========================================

    int ledVoltageADC = analogRead(LED_VOLTAGE_PIN);

    float d9Voltage = ledVoltageADC * 5.0 / 1023.0;

    float ledVoltage = d9Voltage - shuntVoltage;

    if (ledVoltage < 0) {
      ledVoltage = 0;
    }


    // ========================================
    // Рассчитываем сопротивление LED
    // ========================================

    float ledResistance = 0;

    if (current > 0.0001) {
      ledResistance = ledVoltage / current;
    }


    // ========================================
    // Serial Monitor
    // ========================================

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
    Serial.print(ledResistance, 1);
    Serial.println(" Ohm");
  }
}
