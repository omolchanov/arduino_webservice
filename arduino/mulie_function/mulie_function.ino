#include "MultiFunctionDisplay.h"
#include "display_math.h"

#define LATCH_PIN 4
#define CLOCK_PIN 7
#define DATA_PIN 8
#define BTN_LEFT_PIN A1
#define BTN_MIDDLE_PIN A2
#define BTN_RIGHT_PIN A3
#define BUZZER_PIN 3
#define DEBOUNCE_DELAY 50
#define BEEP_MS 30
#define RESET_HOLD_MS 500

MultiFunctionDisplay display(LATCH_PIN, CLOCK_PIN, DATA_PIN);

int counter = 0;

struct ButtonState {
  byte pin;
  bool lastReading;
  bool state;
  unsigned long lastDebounceTime;
};

ButtonState buttons[3] = {
  {BTN_LEFT_PIN, HIGH, HIGH, 0},
  {BTN_MIDDLE_PIN, HIGH, HIGH, 0},
  {BTN_RIGHT_PIN, HIGH, HIGH, 0},
};

void applyCounter() {
  display.show(counter);
  Serial.print("Display: ");
  Serial.println(counter);
}

void setCounter(int value) {
  counter = clamp_counter(value);
  applyCounter();
}

void incrementHundreds() {
  setCounter(increment_hundreds(counter));
}

void incrementTens() {
  setCounter(increment_tens(counter));
}

void incrementOnes() {
  setCounter(increment_ones(counter));
}

void beep() {
  digitalWrite(BUZZER_PIN, LOW);
  delay(BEEP_MS);
  digitalWrite(BUZZER_PIN, HIGH);
}

void resetToBoot() {
  counter = reset_counter();
  display.show(counter);
  Serial.print("Display: ");
  Serial.println(counter);
  beep();
}

bool allButtonsPressed() {
  return digitalRead(BTN_LEFT_PIN) == LOW &&
         digitalRead(BTN_MIDDLE_PIN) == LOW &&
         digitalRead(BTN_RIGHT_PIN) == LOW;
}

void checkResetButtons() {
  static unsigned long pressedAt = 0;
  static bool resetDone = false;

  if (!allButtonsPressed()) {
    pressedAt = 0;
    resetDone = false;
    return;
  }

  if (pressedAt == 0) {
    pressedAt = millis();
    return;
  }

  if (!resetDone && millis() - pressedAt >= RESET_HOLD_MS) {
    resetToBoot();
    resetDone = true;
  }
}

void handleButton(ButtonState &btn, void (*onPress)()) {
  bool reading = digitalRead(btn.pin);

  if (reading != btn.lastReading) {
    btn.lastDebounceTime = millis();
  }

  if ((millis() - btn.lastDebounceTime) > DEBOUNCE_DELAY) {
    if (reading != btn.state) {
      btn.state = reading;
      if (btn.state == LOW) {
        beep();
        onPress();
      }
    }
  }

  btn.lastReading = reading;
}

void handleSerial() {
  if (!Serial.available()) {
    return;
  }

  String line = Serial.readStringUntil('\n');
  line.trim();

  if (line.startsWith("S")) {
    setCounter(line.substring(1).toInt());
    return;
  }

  if (line == "R" || line == "RESET") {
    resetToBoot();
  }
}

void setup() {
  pinMode(BTN_LEFT_PIN, INPUT_PULLUP);
  pinMode(BTN_MIDDLE_PIN, INPUT_PULLUP);
  pinMode(BTN_RIGHT_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, HIGH);

  display.begin();
  Serial.begin(9600);

  resetToBoot();
}

void loop() {
  display.update();

  checkResetButtons();

  if (!allButtonsPressed()) {
    handleButton(buttons[0], incrementHundreds);
    handleButton(buttons[1], incrementTens);
    handleButton(buttons[2], incrementOnes);
  }

  handleSerial();
}
