#define SIGNAL_PIN 8
#define POT_PIN A0
#define LED_PIN 9
#define CURRENT_PIN A1
#define LED_VOLTAGE_PIN A2

#define SHUNT_RESISTOR 10.0

bool signalState = false;
bool undefinedLedState = false;

void setup() {
  pinMode(SIGNAL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  // ==========================================
  // 1. Переключаем логический сигнал
  // ==========================================

  signalState = !signalState;

  digitalWrite(SIGNAL_PIN, signalState);


  // ==========================================
  // 2. Считываем потенциометр
  // ==========================================

  int analogValue = analogRead(POT_PIN);

  float voltage = analogValue * 5.0 / 1023.0;


  // ==========================================
  // 3. Определяем логическую зону
  // ==========================================

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

    // Меняем состояние LED каждую секунду
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


  // ==========================================
  // 4. Измеряем ток через шунт
  // ==========================================

  int currentADC = analogRead(CURRENT_PIN);

  float shuntVoltage = currentADC * 5.0 / 1023.0;

  float current = shuntVoltage / SHUNT_RESISTOR;

  float current_mA = current * 1000.0;


  // ==========================================
  // 5. Измеряем напряжение на D9
  // ==========================================

  int ledVoltageADC = analogRead(LED_VOLTAGE_PIN);

  float d9Voltage = ledVoltageADC * 5.0 / 1023.0;


  // ==========================================
  // 6. Напряжение непосредственно на LED
  // ==========================================

  float ledVoltage = d9Voltage - shuntVoltage;

  if (ledVoltage < 0) {
    ledVoltage = 0;
  }


  // ==========================================
  // 7. Расчёт сопротивления LED
  // ==========================================

  float ledResistance = 0;

  if (current > 0.0001) {
    ledResistance = ledVoltage / current;
  }


  // ==========================================
  // 8. Вывод в Serial Monitor
  // ==========================================

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


  // ==========================================
  // 9. Следующее измерение через 1 секунду
  // ==========================================

  delay(1000);
}
