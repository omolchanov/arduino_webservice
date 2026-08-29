#define SIGNAL_PIN 8
#define POT_PIN A0
#define LED_PIN 9

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

  Serial.println("SIGNAL_PIN: Logic 1 (HIGH)");

  // В течение этой секунды постоянно
  // контролируем потенциометр
  unsigned long startTime = millis();

  while (millis() - startTime < 1000) {

    int analogValue = analogRead(POT_PIN);
    float voltage = analogValue * 5.0 / 1023.0;

    if (voltage < 1.5) {

      // LOW
      analogWrite(LED_PIN, 0);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.println(" V | Logic: 0");

    }
    else if (voltage < 3.0) {

      // НЕОПРЕДЕЛЁННАЯ ЗОНА
      // Мигание реализуем через millis()
      static bool ledState = false;
      static unsigned long lastBlink = 0;

      if (millis() - lastBlink >= 100) {
        lastBlink = millis();
        ledState = !ledState;
      }

      digitalWrite(LED_PIN, ledState);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.println(" V | Logic: UNDEFINED");

    }
    else {

      // HIGH
      int brightness = map(analogValue, 614, 1023, 0, 255);

      analogWrite(LED_PIN, brightness);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.print(" V | Logic: 1 | PWM: ");
      Serial.println(brightness);
    }

    delay(1000);
  }


  // ==========================================
  // ЛОГИЧЕСКИЙ 0 НА SIGNAL_PIN
  // ==========================================

  digitalWrite(SIGNAL_PIN, LOW);

  Serial.println("SIGNAL_PIN: Logic 0 (LOW)");

  // Снова контролируем потенциометр
  startTime = millis();

  while (millis() - startTime < 1000) {

    int analogValue = analogRead(POT_PIN);
    float voltage = analogValue * 5.0 / 1023.0;

    if (voltage < 1.5) {

      analogWrite(LED_PIN, 0);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.println(" V | Logic: 0");

    }
    else if (voltage < 3.0) {

      static bool ledState = false;
      static unsigned long lastBlink = 0;

      if (millis() - lastBlink >= 100) {
        lastBlink = millis();
        ledState = !ledState;
      }

      digitalWrite(LED_PIN, ledState);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.println(" V | Logic: UNDEFINED");

    }
    else {

      int brightness = map(analogValue, 614, 1023, 0, 255);

      analogWrite(LED_PIN, brightness);

      Serial.print("Pot: ");
      Serial.print(voltage, 2);
      Serial.print(" V | Logic: 1 | PWM: ");
      Serial.println(brightness);
    }

    delay(1000);
  }
}
