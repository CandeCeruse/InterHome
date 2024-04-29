#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//Configuración de la red Wifi y la IP de la Raspberry
const char *server = "192.168.75.14";
int port = 1883;
const char *ssid="Nahuel";
const char *passwd = "MIC2018+un";

char serial_command = -1;
unsigned long previousMillis = 0;
unsigned long interval = 30000;

WiFiClient wlanclient;
PubSubClient mqttClient(wlanclient);

String macAddress = WiFi.macAddress();
String clientId = "ESP-Client/" + macAddress;
String topic = "device/light/" + macAddress;

int LED = 2;
int estadoLED = 0;

//Esta funcion publica el estado de la luz de este ESP
String estadoLuz(){
  estadoLED = digitalRead(LED);
  //Si el pin está en HIGH
  if (estadoLED == HIGH){
      String data = "{\"estadoLED\":ON,\"MAC\":\"" + macAddress + "\"}";
      Serial.println(data);
      return data;
  }else {
      //Si el pin está en LOW
      String data = "{\"estadoLED\":OFF,\"MAC\":\"" + macAddress + "\"}";
      Serial.println(data);
      return data;
  }
}

//Función que lee un tópico dce luces y prende o apaga dependiendo del mensaje
void mqttCallback(char *topic, byte *payload, unsigned int length) {
  Serial.println("Message arrived on Topic:");
  Serial.println(topic);

  String estado = "";
  for (int i = 0; i < length; i++) {
    estado += (char)payload[i];
  }
  Serial.println(estado);
  
  if (estado == "ON"){
    digitalWrite(LED, LOW);
  } else {
    digitalWrite(LED, HIGH);
        
  }
  
}


void setup() {
  Serial.begin (115200);
  pinMode(LED, OUTPUT);
  
  WiFi.begin(ssid,passwd);
  Serial.print ("Connecting to AP");
  while(WiFi.status()!=WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }
  Serial.println();
  Serial.println ("Connected to WiFi AP, Got an IP address :");
  Serial.println (WiFi.localIP());
  Serial.print("La MAC del ESP es: ");
  Serial.println(WiFi.macAddress());
  //ACA DEBERIA AGREGAR UNA FORMA DE MANDARLE LA IP 

  String macAddress = WiFi.macAddress();
  String lastWillTopic = "device/disconnected";
  String lastWillMessage = "{\"MAC\":\"" + macAddress + "\"}";
  mqttClient.setServer (server, port);
  
  //Realizar conexión al MQTT Broker
  
  String clientId = "ESP-Client/" + macAddress;
  if (mqttClient.connect(clientId.c_str(), NULL, NULL, lastWillTopic.c_str(), 1, true, lastWillMessage.c_str())) {
    Serial.println ("Connected to MQTT Broker");
    // Publica el tipo de dispositivo al broker MQTT
    String payload = "{\"type\":\"light\", \"MAC\":\"" + macAddress + "\"}"; // Asegúrate de cambiar "light" al tipo de dispositivo correcto
    mqttClient.publish("device/connected", payload.c_str());
  } else {
    Serial.println("MQTT Broker connection failed");
    Serial.println (mqttClient.state());
    delay(200);
  }
  // Suscribirse a los temas
  String topic = "device/light/" + macAddress;
  mqttClient.subscribe(topic.c_str());
  mqttClient.setCallback(mqttCallback);
  
}

void loop() {
  printWifiStatus();
  //verificar si no hay conexión con el broker, si es así reconectarse:
   if(!mqttClient.connected()) {
      reconnect();
  }
  mqttClient.loop();
}


void reconnect() {

  while (!mqttClient.connected()) {
    Serial.println("Trying to connect to the MQTT broker...");

    if(mqttClient.connect(clientId.c_str(), NULL, NULL)) {
      Serial.println ("Connected to MQTT Broker");
      // Publica el tipo de dispositivo al broker MQTT
      String payload = "{\"type\":\"light\", \"MAC\":\"" + macAddress + "\"}"; // Asegúrate de cambiar "light" al tipo de dispositivo correcto
      mqttClient.publish("device/connected", payload.c_str());
      mqttClient.subscribe(topic.c_str());
    } else {
      Serial.print("Fallo, rc=");
      Serial.println (mqttClient.state());
      Serial.println("Trying to connect each 5 seconds");
      delay(5000); 
    }
    printWifiStatus();
  }
}

void printWifiStatus(){
      //print the Wi-Fi status every 30 seconds
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >=interval){
      switch (WiFi.status()){
        case WL_NO_SSID_AVAIL:
          Serial.println("Wifi Configured SSID cannot be reached");
          break;
        case WL_CONNECTED:
          Serial.println("Connection Wifi successfully established");
          break;
        case WL_CONNECT_FAILED:
          Serial.println("Wifi Connection failed");
          break;
      }
      Serial.printf("Connection status: %d\n", WiFi.status());
      Serial.print("RRSI: ");
      Serial.println(WiFi.RSSI());
      previousMillis = currentMillis;
  }
}