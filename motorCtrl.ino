// pins for the MOTORs:
const int m0 = 60;
const int m1 = 61;
const int m2 = 62;
const int m3 = 63;
const int m4 = 64;
const int m5 = 65;


void setup() {
  Serial.begin(9600);
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(m3, OUTPUT);
  pinMode(m4, OUTPUT);
  pinMode(m5, OUTPUT);  
}

void loop() {
  // if there's any serial available, read it:
  while (Serial.available() > 0) {

    int m1v = Serial.parseInt();
    int m2v = Serial.parseInt();
    int m3v = Serial.parseInt();
    int m4v = Serial.parseInt();
    int m5v = Serial.parseInt();

    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
      analogWrite(m1, m1v);
      analogWrite(m2, m2v);
      analogWrite(m3, m3v);
      analogWrite(m4, m4v);
      analogWrite(m5, m5v);
      Serial.print(m1v, HEX);
      Serial.print(m2v, HEX);
      Serial.print(m3v, HEX);
      Serial.print(m4v, HEX);
      Serial.println(m5v, HEX);
    }
  }
}
