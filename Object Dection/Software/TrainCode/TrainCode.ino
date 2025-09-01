char t;

void setup() {
  pinMode(13, OUTPUT);  // left motors forward
  pinMode(12, OUTPUT);  // left motors reverse
  pinMode(11, OUTPUT);  // right motors forward
  pinMode(10, OUTPUT);  // right motors reverse
  pinMode(9, INPUT);
  
  
  
  Serial.begin(9600);
}

void loop() {
  // Remote control commands
  if (Serial.available()) {
    t = Serial.read();
    Serial.println(t);  // Print received command for debugging
  }
  if (t == 'S' || digitalRead(9) == HIGH) {  // STOP
    digitalWrite(13, LOW);
    digitalWrite(12, LOW);
    digitalWrite(11, LOW);
    digitalWrite(10, LOW);
    Serial.println("STOP");
    delay(100);
  }
  else if (t == 'F' || t == '\0') {  // Move forward
    digitalWrite(13, HIGH);
    digitalWrite(12, LOW);
    digitalWrite(11, HIGH);
    digitalWrite(10, LOW);
    Serial.println("Moving Forward");
  }
  if (t == 'B') {  // Move reverse
    digitalWrite(12, HIGH);
    digitalWrite(13, LOW);
    digitalWrite(10, HIGH);
    digitalWrite(11, LOW);
    Serial.println("Moving Backward");
  }
  else if (t == 'L') {  // Turn left
    digitalWrite(13, LOW);
    digitalWrite(12, HIGH); // Stop right motors
    digitalWrite(11, HIGH);
    digitalWrite(10, LOW);
    Serial.println("Turning Left");
  }
  else if (t == 'R') {  // Turn right
    digitalWrite(11, LOW);
    digitalWrite(10, HIGH); // Stop left motors
    digitalWrite(13, HIGH);
    digitalWrite(12, LOW);
    Serial.println("Turning Right");
  }
  
  // else
  // {
  //    digitalWrite(13, HIGH);
  //   digitalWrite(12, LOW);
  //   digitalWrite(11, HIGH);
  //   digitalWrite(10, LOW);
  //   Serial.println("Moving Forward");
  // }

  // Clear command after processing
  t = '\0';

  delay(10);
}