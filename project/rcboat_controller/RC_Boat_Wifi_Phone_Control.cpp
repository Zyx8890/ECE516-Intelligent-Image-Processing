#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "swimgesture"; 
const char* password = "password";

WiFiUDP Udp;
unsigned int localPort = 5005;
char packetBuffer[255];

// Pins
const int ENA = 5;  const int IN1 = 4;  const int IN2 = 14; 
const int ENB = 12; const int IN3 = 13; const int IN4 = 15;

// Speed setting (0-1023)
const int moveSpeed = 800; 

void stopMotors() {
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

void moveForward() {
  analogWrite(ENA, moveSpeed); analogWrite(ENB, moveSpeed);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void turnLeft() {
  analogWrite(ENA, moveSpeed); analogWrite(ENB, moveSpeed);
  digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); // Left motor REV
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); // Right motor FWD
}

void turnRight() {
  analogWrite(ENA, moveSpeed); analogWrite(ENB, moveSpeed);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); // Left motor FWD
  digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); // Right motor REV
}

void setup() {
  Serial.begin(115200);
  int pins[] = {ENA, IN1, IN2, ENB, IN3, IN4};
  for(int i=0; i<6; i++) { pinMode(pins[i], OUTPUT); digitalWrite(pins[i], LOW); }
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  
  Serial.println("\nConnected!");
  Serial.print("IP Address: "); Serial.println(WiFi.localIP());
  
  Udp.begin(localPort);
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    
    String command = String(packetBuffer);
    command.trim();

    if (command == "FORWARD") moveForward();
    else if (command == "LEFT")    turnLeft();
    else if (command == "RIGHT")   turnRight();
    else if (command == "STOP")    stopMotors();
    
    Serial.println("Received: " + command);
  }
}
