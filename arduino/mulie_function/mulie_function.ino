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
#define MODE_TOGGLE_HOLD_MS 3000
#define CLOCK_TICK_MS 60000UL

enum DisplayMode {
  MODE_COUNTER,
  MODE_CLOCK
};

MultiFunctionDisplay display(LATCH_PIN, CLOCK_PIN, DATA_PIN);

int counter = 0;
DisplayMode displayMode = MODE_COUNTER;
int clockMinutes = 720;
unsigned long lastClockTickMs = 0;

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
  display.setClockMode(false);
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

void beepTwice() {
  beep();
  beep();
}

void resetToBoot() {
  counter = reset_counter();
  display.setClockMode(false);
  display.show(counter);
  Serial.print("Display: ");
  Serial.println(counter);
  beep();
}

void emitClockSerial() {
  byte hours;
  byte mins;
  minutes_to_hours_minutes(clockMinutes, hours, mins);
  Serial.print("Clock: ");
  if (hours < 10) {
    Serial.print('0');
  }
  Serial.print(hours);
  Serial.print(':');
  if (mins < 10) {
    Serial.print('0');
  }
  Serial.println(mins);
}

void applyClockDisplay() {
  byte hours;
  byte mins;
  minutes_to_hours_minutes(clockMinutes, hours, mins);
  display.setClockMode(true);
  display.showClock(hours, mins);
}

void setDisplayMode(DisplayMode mode) {
  displayMode = mode;
  if (displayMode == MODE_CLOCK) {
    applyClockDisplay();
    Serial.println("Mode: clock");
  } else {
    applyCounter();
    Serial.println("Mode: counter");
  }
}

void toggleDisplayMode() {
  if (displayMode == MODE_COUNTER) {
    setDisplayMode(MODE_CLOCK);
  } else {
    setDisplayMode(MODE_COUNTER);
  }
  beepTwice();
}

void tickClock() {
  unsigned long now = millis();
  if (lastClockTickMs == 0) {
    lastClockTickMs = now;
    emitClockSerial();
    return;
  }

  if (now - lastClockTickMs < CLOCK_TICK_MS) {
    return;
  }

  lastClockTickMs = now;
  clockMinutes = tick_clock_minutes(clockMinutes);
  emitClockSerial();

  if (displayMode == MODE_CLOCK) {
    applyClockDisplay();
  }
}

bool resetPressed() {
  return digitalRead(BTN_LEFT_PIN) == LOW &&
         digitalRead(BTN_MIDDLE_PIN) == LOW &&
         digitalRead(BTN_RIGHT_PIN) == LOW;
}

void checkResetButton() {
  static unsigned long pressedAt = 0;
  static bool modeToggleDone = false;

  if (!resetPressed()) {
    if (pressedAt != 0 && !modeToggleDone) {
      unsigned long held = millis() - pressedAt;
      if (held >= RESET_HOLD_MS && held < MODE_TOGGLE_HOLD_MS &&
          displayMode == MODE_COUNTER) {
        resetToBoot();
      }
    }
    pressedAt = 0;
    modeToggleDone = false;
    return;
  }

  if (pressedAt == 0) {
    pressedAt = millis();
    return;
  }

  if (!modeToggleDone && millis() - pressedAt >= MODE_TOGGLE_HOLD_MS) {
    toggleDisplayMode();
    modeToggleDone = true;
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

  clockMinutes = clock_start_minutes();
  resetToBoot();
  Serial.println("Mode: counter");
}

void loop() {
  display.update();
  tickClock();
  checkResetButton();

  if (!resetPressed() && displayMode == MODE_COUNTER) {
    handleButton(buttons[0], incrementHundreds);
    handleButton(buttons[1], incrementTens);
    handleButton(buttons[2], incrementOnes);
  }

  handleSerial();
}
