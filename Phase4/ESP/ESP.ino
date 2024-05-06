#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h> 

#define D8_PIN 15
#define D0_PIN 16

MFRC522 rfid(D8_PIN, D0_PIN); // Instance of the class

/*
 * TESTING
 * DO NOT RUN
 */

MFRC522::MIFARE_Key key;
/*
const char* ssid = "TP-Link_2AD8";
const char* password = "14730078";
const char* mqtt_server = "192.168.0.102";


WiFiClient espClient;
PubSubClient client(espClient);

const int photoresistorPin = A0;
const char* topic = "light_intensity";

// Init array that will store new NUID
byte nuidPICC[4];

// MQTT topic names
const char* light_topic = "light_intensity";
const char* rfid_topic = "rfid_data";

void setup_wifi() {
  delay(10);
  Serial.begin(115200);
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
      Serial.println("connected to MQTT");
    } else {
      Serial.print("failed to connect, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}

*/
void setup() {
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  
  // Init SPI bus
  SPI.begin();     
  rfid.PCD_Init(); // Init MFRC522
      
  pinMode(photoresistorPin, INPUT);

   Serial.print(F("Reader :"));
   rfid.PCD_DumpVersionToSerial();
    for (byte i = 0; i < 6; i++)
    {
        key.keyByte[i] = 0xFF;
    }
    /*
    Serial.println(F("This code scan the MIFARE Classic NUID."));
    Serial.print(F("Using the following key:"));
    printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
    */
}

/**
 Helper routine to dump a byte array as hex values to Serial.
*/
void printHex(byte *buffer, byte bufferSize)
{
    for (byte i = 0; i < bufferSize; i++)
    {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}
/**
 Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte *buffer, byte bufferSize)
{
    for (byte i = 0; i < bufferSize; i++)
    {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], DEC);
    }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

   // Read and publish photoresistor data
  int lightIntensity = analogRead(photoresistorPin);
  client.publish(light_topic, String(lightIntensity).c_str());
  Serial.println(lightIntensity);

  // RFID scanning
    if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
        // Get RFID UID in hexadecimal
        Serial.print("RFID UID (Hex): ");
        printHex(rfid.uid.uidByte, rfid.uid.size);

        // Get RFID UID in decimal
        Serial.print("RFID UID (Dec): ");
        printDec(rfid.uid.uidByte, rfid.uid.size);

        // Create a hex string for MQTT
        char rfid_uid[20];
        snprintf(rfid_uid, sizeof(rfid_uid), "%02X%02X%02X%02X",
                 rfid.uid.uidByte[0],
                 rfid.uid.uidByte[1],
                 rfid.uid.uidByte[2],
                 rfid.uid.uidByte[3]);

        // Publish RFID UID to MQTT
        client.publish("rfid_data", rfid_uid);

        rfid.PICC_HaltA(); // Halt the current tag
    }

  delay(1000); // adjust delay as needed
}
