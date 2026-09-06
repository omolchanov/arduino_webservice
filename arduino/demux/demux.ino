// DEMUX 1-to-2 — standalone sketch for Arduino IDE
// Wiring:
//   D2 (DI), D4 (A) — jumper to GND (=0); open or 5V (=1, internal pull-up)
//   D11 (Y0), D12 (Y1) — each --[220 Ohm]-- LED (+) -- LED (-) -- GND

#define PIN_DI 2
#define PIN_A  4
#define PIN_Y0 11
#define PIN_Y1 12

unsigned long lastPrintTime = 0;
const unsigned long printInterval = 2000;

bool demux_y0(bool a, bool di) {
  return !a && di;
}

bool demux_y1(bool a, bool di) {
  return a && di;
}

void setup() {
  pinMode(PIN_DI, INPUT_PULLUP);
  pinMode(PIN_A,  INPUT_PULLUP);
  pinMode(PIN_Y0, OUTPUT);
  pinMode(PIN_Y1, OUTPUT);

  Serial.begin(9600);
  Serial.println("DEMUX 1-to-2  |  A -> selects Y0 (0) or Y1 (1)");
  Serial.println("Pins: DI=D2, A=D4 (GND=0, open/5V=1), Y0=D11, Y1=D12 -> 220R -> LED -> GND");
  Serial.println("----------------------------------------------");
}

void loop() {
  bool a  = digitalRead(PIN_A);
  bool di = digitalRead(PIN_DI);

  bool y0 = demux_y0(a, di);
  bool y1 = demux_y1(a, di);
  digitalWrite(PIN_Y0, y0);
  digitalWrite(PIN_Y1, y1);

  if (millis() - lastPrintTime >= printInterval) {
    lastPrintTime = millis();

    Serial.print("A=");
    Serial.print(a);
    Serial.print("  DI=");
    Serial.print(di);
    Serial.print("  ->  Y0=");
    Serial.print(y0);
    Serial.print("  Y1=");
    Serial.print(y1);
    Serial.print("  (selected: Y");
    Serial.print(a ? "1" : "0");
    Serial.println(")");
  }
}
