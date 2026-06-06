#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pin configuration (modify if using different wiring)
#define trigPin 9
#define echoPin 10
#define irPin 6

LiquidCrystal_I2C lcd(0x27, 16, 2);

long duration;
float distance;

String incomingText = "";

void setup() {
  Serial.begin(115200);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(irPin, INPUT);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Gesture Control");

  lcd.setCursor(0, 1);
  lcd.print("System Ready");

  delay(2000);
  lcd.clear();
}

float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH, 20000);

  if (duration == 0) return 999.0;

  return duration * 0.0343 / 2;
}

void updateLCD(String line1, String line2) {
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print(line1.substring(0, 16));

  lcd.setCursor(0, 1);
  lcd.print(line2.substring(0, 16));
}

void loop() {

  // Send sensor data to python
  distance = getDistance();

  int ir = (digitalRead(irPin) == LOW) ? 1 : 0;

  Serial.print(distance);
  Serial.print(",");
  Serial.println(ir);

  // Receive LCD data from python
  if (Serial.available()) {

    incomingText = Serial.readStringUntil('\n');

    int separatorIndex = incomingText.indexOf('|');

    if (separatorIndex != -1) {

      String line1 = incomingText.substring(0, separatorIndex);
      String line2 = incomingText.substring(separatorIndex + 1);

      updateLCD(line1, line2);
    }
  }

  delay(30);
}