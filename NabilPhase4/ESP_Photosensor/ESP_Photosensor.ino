#include <ESP8266WiFi.h>
#include <PubSubClient.h>

/*
const char* ssid = "TP-Link_2AD8";
const char* password = "14730078";
const char* mqtt_server = "192.168.0.102";
*/

const char* ssid = "LHE786";
const char* password = "aida2432";
const char* mqtt_server = "192.168.2.38";


WiFiClient espClient;
PubSubClient client(espClient);

const int photoresistorPin = A0;
const char* topic = "light_intensity";

void setup() {
  pinMode(photoresistorPin, INPUT);
  Serial.begin(115200);
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
  int lightIntensity = analogRead(photoresistorPin);
  Serial.println(lightIntensity);
  client.publish(topic, String(lightIntensity).c_str());
  delay(1000); // adjust delay as needed
}
