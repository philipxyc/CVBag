#include "SoftPWM.h"

// pins for the MOTORs:
const int m0 = 60;
const int m1 = 61;
const int m2 = 62;
const int m3 = 63;
const int m4 = 64;


void setup() {
  Serial2.begin(9600);
  SoftPWMBegin();
  pinMode(m0, OUTPUT);  
  pinMode(m1, OUTPUT);
  pinMode(m2, OUTPUT);
  pinMode(m3, OUTPUT);
  pinMode(m4, OUTPUT);
}

void loop() {
  // if there's any serial available, read it:
  while (Serial2.available() > 0) {

    int m0v = Serial2.parseInt();
    int m1v = Serial2.parseInt();
    int m2v = Serial2.parseInt();
    int m3v = Serial2.parseInt();
    int m4v = Serial2.parseInt();

    // look for the newline. That's the end of your sentence:
    if (Serial2.read() == ']') {
      SoftPWMSet(m0, m0v);
      SoftPWMSet(m1, m1v);
      SoftPWMSet(m2, m2v);
      SoftPWMSet(m3, m3v);
      SoftPWMSet(m4, m4v);
      Serial2.print(m0v);
      Serial2.print(m1v);
      Serial2.print(m2v);
      Serial2.print(m3v);
      Serial2.println(m4v);
    }
  }
}