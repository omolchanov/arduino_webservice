#include "sensor_math.h"

#define TRIG_PIN 9
#define ECHO_PIN 10
#define LDR_PIN A0
#define LM35_PIN A3

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = distanceCm(duration);

  Serial.print("Distance: ");
  Serial.print(distance, 1);
  Serial.println(" cm");

  int light = invertLight(analogRead(LDR_PIN));

  Serial.print("Light: ");
  Serial.println(light);

  int lm35Value = analogRead(LM35_PIN);
  float temperature = tempC(lm35Value);

  Serial.print("Temperature: ");
  Serial.print(temperature, 1);
  Serial.println(" C");

  Serial.println("--------------------");
  delay(1000);
}
