#define SIGNAL_PIN 8
#define POT_PIN A0
#define LED_PIN 9
#define CURRENT_PIN A1

#define SHUNT_RESISTOR 10.0

void setup() {
  pinMode(SIGNAL_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  // ==========================================
  // ЛОГИЧЕСКАЯ 1 НА SIGNAL_PIN
  // ==========================================

  digitalWrite(SIGNAL_PIN, HIGH);

  Serial.println();
  Serial.println("SIGNAL_PIN: Logic 1 (HIGH)");

  unsigned long startTime = millis();

  while (millis() - startTime < 1000) {
    processPotentiometer();

    delay(1000);
  }


  // ==========================================
  // ЛОГИЧЕСКИЙ 0 НА SIGNAL_PIN
  // ==========================================

  digitalWrite(SIGNAL_PIN, LOW);

  Serial.println();
  Serial.println("SIGNAL_PIN: Logic 0 (LOW)");

  startTime = millis();

  while (millis() - startTime < 1000) {
    processPotentiometer();

    delay(1000);
  }
}


// ==========================================
// ОБРАБОТКА ПОТЕНЦИОМЕТРА
// ==========================================

void processPotentiometer() {

  int analogValue = analogRead(POT_PIN);

  float voltage = analogValue * 5.0 / 1023.0;


  // ==========================================
  // ЗОНА LOW
  // ==========================================

  if (voltage < 1.5) {

    analogWrite(LED_PIN, 0);

    printValues(voltage, 0);

  }


  // ==========================================
  // НЕОПРЕДЕЛЁННАЯ ЗОНА
  // ==========================================

  else if (voltage < 3.0) {

    static bool ledState = false;
    static unsigned long lastBlink = 0;

    if (millis() - lastBlink >= 100) {
      lastBlink = millis();
      ledState = !ledState;
    }

    digitalWrite(LED_PIN, ledState);

    printValues(voltage, 0);

  }


  // ==========================================
  // ЗОНА HIGH
  // ==========================================

  else {

    int brightness = map(
      analogValue,
      614,
      1023,
      0,
      255
    );

    analogWrite(LED_PIN, brightness);

    printValues(voltage, brightness);
  }
}


// ==========================================
// ИЗМЕРЕНИЕ И ВЫВОД ТОКА
// ==========================================

void printValues(float potentiometerVoltage, int pwm) {

  // Измеряем напряжение на шунте
  int currentADC = analogRead(CURRENT_PIN);

  float shuntVoltage = currentADC * 5.0 / 1023.0;

  // Закон Ома
  float current = shuntVoltage / SHUNT_RESISTOR;

  // Переводим A → mA
  float current_mA = current * 1000.0;


  Serial.print("Pot: ");
  Serial.print(potentiometerVoltage, 2);
  Serial.print(" V | ");

  if (potentiometerVoltage < 1.5) {
    Serial.print("Logic: 0");
  }
  else if (potentiometerVoltage < 3.0) {
    Serial.print("Logic: UNDEFINED");
  }
  else {
    Serial.print("Logic: 1");
  }

  Serial.print(" | PWM: ");
  Serial.print(pwm);

  Serial.print(" | Shunt: ");
  Serial.print(shuntVoltage, 3);
  Serial.print(" V");

  Serial.print(" | Current: ");
  Serial.print(current_mA, 1);
  Serial.println(" mA");
}
