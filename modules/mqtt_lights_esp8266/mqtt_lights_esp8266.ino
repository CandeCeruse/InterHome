#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//Configuración de la red Wifi y la IP de la Raspberry
const char *server = "10.3.141.1";

int port = 1883;
const char *ssid="InterHome";
const char *passwd = "interhome";

char serial_command = -1;
unsigned long previousMillis = 0;
unsigned long interval = 30000;
unsigned long intervalState = 2000;

WiFiClient wlanclient;
PubSubClient mqttClient(wlanclient);

String macAddress = WiFi.macAddress();
String clientId = "ESP-Client/" + macAddress;
String topic = "device/light/" + macAddress;
String label = "Cocina";

int LED = 4; // D2 (Estamos usando el BUILTIN, pero si es necesario cambiar)
int PIN_BUTTON = 5; //D1
int ledState = 0;
int buttonOld = 0;
int buttonNew = 0;

//Esta funcion publica el estado de la luz de este ESP
String estadoLuz(){
  int estadoLED = digitalRead(LED);
  //Si el pin está en HIGH
  if (estadoLED == LOW){
      String data = "{\"state\":\"ON\", \"MAC\":\"" + macAddress + "\"}";
      return data;
  }else if(estadoLED == HIGH){
      //Si el pin está en LOW
      String data = "{\"state\":\"OFF\", \"MAC\":\"" + macAddress + "\"}";
      return data;
  }else{
      return "{\"error\":\"Estado desconocido\"}";
  }
}

void buttonLight(){
  buttonNew = digitalRead(PIN_BUTTON);
  delay(10);
  if (buttonNew != buttonOld){
    buttonOld = buttonNew;
    if(buttonNew == LOW){
      ledState = !ledState;
      digitalWrite(LED, ledState);
    }
  }
}

//Función que lee un tópico dce luces y prende o apaga dependiendo del mensaje
void mqttCallback(char *topic, byte *payload, unsigned int length) {
  String estado = "";
  for (int i = 0; i < length; i++) {
    estado += (char)payload[i];
  }
  if (estado == "OFF"){
    digitalWrite(LED, LOW);
  } else {
    digitalWrite(LED, HIGH);  
  }
}


void setup() {
  Serial.begin (115200);
  pinMode(PIN_BUTTON, INPUT); // Configura el pin del pulsador como entrada
  pinMode(LED, OUTPUT); // Configura el pin del LED como salida
  digitalWrite(LED,ledState);

  WiFi.begin(ssid,passwd);
  Serial.print ("Connecting to AP");
  while(WiFi.status()!=WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }
  Serial.println();
  Serial.println ("Connected to WiFi AP, Got an IP address :");
  Serial.println (WiFi.localIP());
  String lastWillTopic = "device/disconnected";
  String lastWillMessage = "{\"MAC\":\"" + macAddress + "\"}";
  mqttClient.setServer (server, port);
  
  //Realizar conexión al MQTT Broker
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
  mqttClient.subscribe(topic.c_str());
  mqttClient.setCallback(mqttCallback);
}


void loop() {
  buttonLight();
  String data = estadoLuz();
  // Convierto la cadena de caracteres a un array de caracteres.
  char dataChar[data.length() + 1];
  data.toCharArray(dataChar, sizeof(dataChar));

  unsigned long currentMillis = millis();
  if(currentMillis - previousMillis >= intervalState){
    previousMillis = currentMillis;
    mqttClient.publish("device/light/state", dataChar);
  }
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
