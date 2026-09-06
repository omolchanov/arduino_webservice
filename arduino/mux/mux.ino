// MUX 2-to-1 — standalone sketch for Arduino IDE
// Wiring:
//   D2 (DI0), D3 (DI1), D4 (A) — jumpers to 5V (=1) or GND (=0)
//   D13 (DO) --[220 Ohm]-- LED (+) -- LED (-) -- GND

#define PIN_DI0 2
#define PIN_DI1 3
#define PIN_A   4
#define PIN_DO  13

unsigned long lastPrintTime = 0;
const unsigned long printInterval = 2000;

bool mux2to1(bool a, bool di0, bool di1) {
  return a ? di1 : di0;
}

void setup() {
  pinMode(PIN_DI0, INPUT_PULLUP);
  pinMode(PIN_DI1, INPUT_PULLUP);
  pinMode(PIN_A,   INPUT_PULLUP);
  pinMode(PIN_DO,  OUTPUT);

  Serial.begin(9600);
  Serial.println("MUX 2-to-1  |  A -> selects DI0 (0) or DI1 (1)");
  Serial.println("Pins: DI0=D2, DI1=D3, A=D4, DO=D13 -> 220R -> LED -> GND");
  Serial.println("----------------------------------------------");
}

void loop() {
  bool a   = digitalRead(PIN_A);
  bool di0 = digitalRead(PIN_DI0);
  bool di1 = digitalRead(PIN_DI1);

  bool out = mux2to1(a, di0, di1);
  digitalWrite(PIN_DO, out);

  if (millis() - lastPrintTime >= printInterval) {
    lastPrintTime = millis();

    Serial.print("A=");
    Serial.print(a);
    Serial.print("  DI0=");
    Serial.print(di0);
    Serial.print("  DI1=");
    Serial.print(di1);
    Serial.print("  ->  DO=");
    Serial.print(out);
    Serial.print("  (selected: DI");
    Serial.print(a ? "1" : "0");
    Serial.println(")");
  }
}
