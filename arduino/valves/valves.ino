#include "valve_logic.h"

const int INPUT_A = 2;
const int INPUT_B = 3;
const int OUTPUT_Y = 9;

String selectedGate = "AND";

unsigned long lastPrintTime = 0;

const unsigned long printInterval = 1000;

void setup() {
  pinMode(INPUT_A, INPUT_PULLUP);
  pinMode(INPUT_B, INPUT_PULLUP);

  pinMode(OUTPUT_Y, OUTPUT);

  Serial.begin(9600);

  Serial.println("=================================");
  Serial.println("   ЛОГИЧЕСКИЕ ВЕНТИЛИ");
  Serial.println("=================================");
  Serial.println();
  Serial.println("Выберите вентиль:");
  Serial.println("AND  - И");
  Serial.println("OR   - ИЛИ");
  Serial.println("NOT  - НЕ");
  Serial.println("NAND - И-НЕ");
  Serial.println("NOR  - ИЛИ-НЕ");
  Serial.println("XOR  - исключающее ИЛИ");
  Serial.println("XNOR - исключающее ИЛИ-НЕ");
  Serial.println();
  Serial.println("По умолчанию выбран AND");
  Serial.println();
}

void loop() {

  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');

    command.trim();
    command.toUpperCase();

    if (command == "AND" ||
        command == "OR" ||
        command == "NOT" ||
        command == "NAND" ||
        command == "NOR" ||
        command == "XOR" ||
        command == "XNOR") {

      selectedGate = command;

      Serial.print("Выбран вентиль: ");
      Serial.println(selectedGate);
      Serial.println();
    }
    else {
      Serial.println("Неизвестная команда.");
      Serial.println("Используйте: AND, OR, NOT, NAND, NOR, XOR или XNOR");
      Serial.println();
    }
  }

  bool A = !digitalRead(INPUT_A);
  bool B = !digitalRead(INPUT_B);

  bool Y = evalGate(selectedGate.c_str(), A, B);

  digitalWrite(OUTPUT_Y, Y);

  if (millis() - lastPrintTime >= printInterval) {

    lastPrintTime = millis();

    Serial.print("A = ");
    Serial.print(A);

    Serial.print(" | B = ");
    Serial.print(B);

    Serial.print(" | Y = ");
    Serial.print(Y);

    Serial.print(" | Gate = ");
    Serial.println(selectedGate);
  }
}
