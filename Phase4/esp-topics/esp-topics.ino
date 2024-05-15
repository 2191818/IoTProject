#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials
const char* ssid = "iPhone";
const char* password = "Hibba2000";
/*
const char* ssid = "BELL485";
const char* password = "Amin1966";
*/

/*
const char* ssid = "LHE786";
const char* password = "aida2432";
*/

/* 
 *  Data-Wifi
const char* ssid = "Dolphin";
const char* password = "nnnnnnnn";
*/

/*
const char* ssid = "TP-Link_2AD8";
const char* password = "14730078";
*/



// MQTT broker
const char* mqtt_server = "172.20.10.11";
//const char* mqtt_server = "192.168.2.32";
//const char* mqtt_server = "192.168.2.38";
//const char* mqtt_server = "192.168.0.137";
//const char* mqtt_server = "172.20.10.4";

// MQTT topics
const char* topic_light_intensity = "light_intensity";
const char* topic_nuid_dec = "nuid_dec";

// Photoresistor pin
const int photoresistorPin = A0;

// RFID pins
#define D8_PIN 15
#define D0_PIN 16

WiFiClient espClient;
PubSubClient client(espClient);

MFRC522 rfid(D8_PIN, D0_PIN); // RFID reader instance
MFRC522::MIFARE_Key key;

byte nuidPICC[4]; // Array to store the NUID tag

void setup() {
  Serial.begin(115200);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init RFID reader
  Serial.println();
  Serial.println(F("Reader:"));
  rfid.PCD_DumpVersionToSerial();
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  // Connect to WiFi
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read light intensity
  int lightIntensity = analogRead(photoresistorPin);
  Serial.println(lightIntensity);
  client.publish(topic_light_intensity, String(lightIntensity).c_str());

  // RFID reading
  if (rfid.PICC_IsNewCardPresent()) {
    if (rfid.PICC_ReadCardSerial()) {
      Serial.print(F("PICC type: "));
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      Serial.println(rfid.PICC_GetTypeName(piccType));

      if (piccType == MFRC522::PICC_TYPE_MIFARE_MINI ||
          piccType == MFRC522::PICC_TYPE_MIFARE_1K ||
          piccType == MFRC522::PICC_TYPE_MIFARE_4K) {
        Serial.println(F("Your tag is of type MIFARE Classic."));
        
        Serial.println(F("A card has been detected."));

        // Store NUID into nuidPICC array
        for (byte i = 0; i < 4; i++) {
          nuidPICC[i] = rfid.uid.uidByte[i];
        }

        Serial.println(F("The NUID tag is:"));
        Serial.print(F("In dec: "));
        printDec(rfid.uid.uidByte, rfid.uid.size);
        Serial.println();

        // Publish NUID tag in dec format
        String nuid_dec = byteArrayToDecimalString(rfid.uid.uidByte, rfid.uid.size);
        client.publish(topic_nuid_dec, nuid_dec.c_str());
        
      } else {
        Serial.println(F("Your tag is not of type MIFARE Classic."));
      }
    }

    // Halt PICC
    rfid.PICC_HaltA();
    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();
  }

  delay(1000); // Adjust delay as needed
}


void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}

String byteArrayToDecimalString(byte *buffer, byte bufferSize) {
  String decimalString = "";
  for (byte i = 0; i < bufferSize; i++) {
    decimalString += String(buffer[i]);
    decimalString += " ";
  }
  return decimalString;
}
