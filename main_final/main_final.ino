/*
   line connect
   NodeCMU  -   Arduino Uno
   D1       -   A5
   D2       -   A4
   GND      -   GND (importain)
   [D4       -   Servo ]
   
   Arduino Uno  - MFRC522
   9            - Reset (RST)
   10           - SDA
   11           - MOSI
   12           - MISO
   13           - SCK
   3.3V         - VCC

   Servo SG90 connection
   Red - Arduino Uno VCC (5V)
   Brown - Arduino Uno GND
   Orange - Node MCU D4
*/


#include <ESP8266WiFi.h>
#include <WebSocketsServer.h>
#include <ESP8266WiFiMulti.h>
#include <String>
#include <Wire.h>
#include <Hash.h>
#include <Servo.h>


//debug Serial code
#define DEBUG_ESP_PORT
#define DEBUG_WEBSOCKETS

#ifdef DEBUG_WEBSOCKETS
#define DEBUG_MSG(...) DEBUG_WEBSOCKETS.printf( __VA_ARGS__ )
#else
#define DEBUG_MSG(...)
#endif

//define library
ESP8266WiFiMulti WiFiMulti;
const char* ssid     = "29/5 Lầu 3";
const char* password = "68686868";
String _respond1 , _respond2;
Servo myservo;

//enable websocker server
WebSocketsServer webSocket = WebSocketsServer(81);

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t lenght) {
  Serial.printf("[%u] get Message: %s\r\n", num, payload);
  switch (type) {
    case WStype_DISCONNECTED:
      //listening flag
      Serial.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED:
      //listening connect
      {
        IPAddress ip = webSocket.remoteIP(num);
        Serial.printf("[%u] Connected from %d.%d.%d.%d url: %s\r\n", num, ip[0], ip[1], ip[2], ip[3], payload);
      }
      break;

    case WStype_TEXT:
      //listening TEXT : importain
      {
        //Serial.printf("[%u] get Text: %s\r\n", num, payload);
        //receive TEXT
        String _payload = String((char *) &payload[0]);
        Serial.println(_payload);

        String temp = (_payload.substring(_payload.indexOf(":") + 2, _payload.length()));
        String ID = (temp.substring(0, temp.indexOf(",")));
        //Serial.println(temp);
        Serial.print("ID hien tai: "); Serial.println(ID);

        temp = (temp.substring(temp.indexOf(":") + 3, temp.length()));
        String plateID = (temp.substring(0, temp.indexOf(",") - 1 ));
        //Serial.println(temp);
        Serial.print("plateID hien tai: "); Serial.println(plateID);

        temp = (temp.substring(temp.indexOf(":") + 3, temp.length()));
        String RFID = (temp.substring(0, temp.indexOf(",") - 1 ));
        //Serial.println(temp);
        Serial.print("RFID hien tai: "); Serial.println(RFID);

        temp = (temp.substring(temp.indexOf(":") + 2, temp.length()));
        int _status = (temp.substring(0, temp.indexOf("}") )).toInt();
        //Serial.println(temp);
        Serial.print("status hien tai: "); Serial.println(_status);

        //creat string respond

        _respond1 = "";
        _respond1.concat(ID);
        _respond1.concat('|');
        _respond1.concat(plateID);
        _respond1.concat('|');
        _respond2 = _respond1;
        //if _status 1 => check out, 0 => check in
        switch (_status)
        {
          case 1:
            {
              //check RFID
              String a = filterRFID();
              if (a == RFID) {
                Serial.println(a);
                Serial.print(_respond1);
                //cho nay them ham quay Servo
                _respond1.concat(RFID);
                _respond1.concat('|');
                _respond1.concat("1");
                //id plateid rfid checkout =1
                Serial.print(_respond1);
                webSocket.broadcastTXT(_respond1);
                _servo();
              }
              else {
                Serial.println(a);
                Serial.print("Dang check-out thi sai the => FAIL");
                _respond1.concat(RFID);
                _respond1.concat('|');
                _respond1.concat("2");
                webSocket.broadcastTXT(_respond1);
              }
            }
            break;
          case 0:
            {
              String b = filterRFID();
              Serial.print("Dang check-in");
              _respond2.concat(b);
              _respond2.concat("|0");
              webSocket.broadcastTXT(_respond2);
              Serial.println(_respond2);
              _servo();
            }
            break;
          default:
            // if nothing else matches, do the default
            // default is optional
            break;
        }
        //status = 1 -> checkin = 1, checkout = 0 -> đang checkout -> uno quẹt rfid
        //-> so sánh rfid vừa quẹt với rfid trong api1 -> quay servo (trùng)
        //-> gửi ID, biển số, checkout = 1, checkoutTime về lap

        //status = 0 ->ID nul, checkin = null, checkout = null, plateID null, all null
        //-> dang checkin -> uno rfid -> quay servo
        //-> update biển số, rfid, checkin = 1, checkinTime -> gửi về lap -> tạo row mới trên dtb.
      }
      break;
  }
}

void setup() {
  // put your setup code here, to run once:
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  //WiFi.begin(ssid, password);

  for (uint8_t t = 4; t > 0; t--) {
    Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
    Serial.flush();
    delay(1000);
  }

  ///call servo
  myservo.attach(2);
  //connect multi wwifi
  WiFiMulti.addAP(ssid, password);

  while (WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("Start Websocket Server");
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();
}


String filterRFID() {
  String a;
  String test;
  do {
    a = _masterGetRFID();
    test = a;
  } while (test.substring(0, 1) != " ");
  return a;
}


String _masterGetRFID()
{
  Serial.println("get RFID");
  String result = "";
  Wire.requestFrom(8, 12);    // request 6 bytes from slave device #8
  while (Wire.available()) { // slave may send less than requested
    char c = Wire.read(); // receive a byte as character
    //Serial.print(c);         // print the character
    result.concat(c);
  }
  delay(500);
  return result;
}

void _servo() {
  myservo.write(0);
  delay(1000);
  myservo.write(90);
  delay(1000);
}
