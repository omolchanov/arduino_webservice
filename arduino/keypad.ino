const byte rowPins[4] = {2, 3, 4, 5};
const byte colPins[4] = {6, 7, 8, 9};

const char keys[4][4] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

void setup() {
  Serial.begin(9600);

  for (byte r = 0; r < 4; r++) {
    pinMode(rowPins[r], OUTPUT);
    digitalWrite(rowPins[r], HIGH);
  }

  for (byte c = 0; c < 4; c++) {
    pinMode(colPins[c], INPUT_PULLUP);
  }
}

void loop() {
  for (byte r = 0; r < 4; r++) {
    digitalWrite(rowPins[r], LOW);
    delayMicroseconds(100);

    for (byte c = 0; c < 4; c++) {
      if (digitalRead(colPins[c]) == LOW) {
        delay(20);

        if (digitalRead(colPins[c]) == LOW) {
          Serial.println(keys[r][c]);

          while (digitalRead(colPins[c]) == LOW) {
            delay(10);
          }
        }
      }
    }

    digitalWrite(rowPins[r], HIGH);
  }
}
