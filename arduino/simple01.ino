#define SIGNAL_PIN 8
#define POT_PIN A0
#define LED_LOGIC_PIN 9

void setup() {

  pinMode(SIGNAL_PIN, OUTPUT);
  pinMode(LED_LOGIC_PIN, OUTPUT);

  Serial.begin(9600);
}

void loop() {

  // Считываем потенциометр
  int analogValue = analogRead(POT_PIN);

  // Переводим значение ADC в напряжение
  float voltage = analogValue * 5.0 / 1023.0;

  // Определяем логическое состояние
  // Пока используем середину диапазона как порог
  bool logicState = voltage >= 2.5;

  // -------------------------
  // Генерируем логическую 1
  // -------------------------

  digitalWrite(SIGNAL_PIN, HIGH);

  Serial.print("Generated: 1 | ");
  Serial.print("Potentiometer: ");
  Serial.print(voltage, 2);
  Serial.print(" V | ");

  if (logicState) {
    Serial.println("Detected: 1");
    digitalWrite(LED_LOGIC_PIN, HIGH);
  } else {
    Serial.println("Detected: 0");
    digitalWrite(LED_LOGIC_PIN, LOW);
  }

  delay(1000);


  // -------------------------
  // Генерируем логический 0
  // -------------------------

  digitalWrite(SIGNAL_PIN, LOW);

  Serial.print("Generated: 0 | ");
  Serial.print("Potentiometer: ");
  Serial.print(voltage, 2);
  Serial.print(" V | ");

  if (logicState) {
    Serial.println("Detected: 1");
    digitalWrite(LED_LOGIC_PIN, HIGH);
  } else {
    Serial.println("Detected: 0");
    digitalWrite(LED_LOGIC_PIN, LOW);
  }

  delay(1000);
}
