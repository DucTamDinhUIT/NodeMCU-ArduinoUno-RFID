#include <Wire.h>

void setup() {
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(115200);  // start serial for output
}

void loop() {
  String a;
  do {
    a = _masterGetRFID();
  } while (a.substring(0, 1) != " ");
  Serial.println(a);
  delay(1000);
}

String _masterGetRFID()
{
  Wire.requestFrom(8, 12);    // request 6 bytes from slave device #8
  String result = "";
  while (Wire.available()) { // slave may send less than requested
    char c = Wire.read(); // receive a byte as character
    //Serial.print(c);         // print the character
    result.concat(c);
  }
  //Serial.println(result);
  return result;
}
