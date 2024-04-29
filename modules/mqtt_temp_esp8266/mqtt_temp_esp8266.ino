#include <DHT11.h>
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

DHT11 dht11(2);

const char *server = "192.168.1.19";
int port = 1883;
const char *ssid="Wifi01";
const char *passwd = "k0z7m1gus";

char serial_command = -1;
unsigned long previousMillis = 0;
unsigned long interval = 30000;

WiFiClient wlanclient;
PubSubClient mqttClient(wlanclient);

String macAddress = WiFi.macAddress();
String clientId = "ESP-Client/" + macAddress;
String topic = "device/temperature/" + macAddress;

String temperatura(){
  int temperatura = 0;
  int humedad = 0;
  int error = 600;
    // Lee los valores de temperatura y humedad con la funcion de la libreria
  int resultado = dht11.readTemperatureHumidity(temperatura, humedad);
    
  //Si dio como resultado 0 significa que funciono bien el sensor
  if (resultado == 0) {
      String data = "{\"temperature\":" + String(temperatura) + ",\"humidity\":" + String(humedad) + ",\"MAC\":\"" + macAddress + "\"}";
      //Serial.println(data);
      return data;
  } else {
      //Si no pudo leer el sensor tira error 600
      Serial.println(DHT11::getErrorString(resultado));
      return "{\"error\":\"" + String(error) +"\"}";
  }
}

void mqttCallback(char *topic, byte *payload, unsigned int length) {
  Serial.println("Message arrived on Topic:");
  Serial.println(topic);

  // Convierte el payload a una cadena de caracteres
  char message[length + 1]; // +1 para el carácter nulo
  memcpy(message, payload, length);
  message[length] = '\0'; // Añade el carácter nulo al final

}


void setup() {
  Serial.begin (115200);
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
  
  String lastWillTopic = "device/disconnected";
  String lastWillMessage = "{\"MAC\":\"" + macAddress + "\"}";
  mqttClient.setServer (server, port);

  if(mqttClient.connect(clientId.c_str(), NULL, NULL, lastWillTopic.c_str(), 1, true, lastWillMessage.c_str())) {
    Serial.println ("Connected to MQTT Broker");
    // Publica el tipo de dispositivo al broker MQTT
    String payload = "{\"type\":\"temperature\", \"MAC\":\"" + macAddress + "\"}"; // Asegúrate de cambiar "light" al tipo de dispositivo correcto
    mqttClient.publish("device/connected", payload.c_str());
  } else {
    Serial.println("MQTT Broker connection failed");
    Serial.println (mqttClient.state());
    delay(200);
  }
  // Suscribirse a los temas
  mqttClient.setCallback(mqttCallback);
}


void loop() {
  
  String data = temperatura();
  Serial.println(data);
  // Convierto la cadena de caracteres a un array de caracteres.
  char dataChar[data.length() + 1];
  data.toCharArray(dataChar, sizeof(dataChar));
  mqttClient.publish("temp", dataChar);

  printWifiStatus();
    //verificar si no hay conexión con el broker, si es así reconectarse:
   if(!mqttClient.connected()) {
      reconnect();
  }
  mqttClient.loop();
  delay(2000);
}


void reconnect() {

  while (!mqttClient.connected()) {
    Serial.println("Trying to connect to the MQTT broker...");

    if(mqttClient.connect(clientId.c_str(), NULL, NULL)) {
      Serial.println ("Connected to MQTT Broker");
      // Publica el tipo de dispositivo al broker MQTT
      String payload = "{\"type\":\"temperature\", \"MAC\":\"" + macAddress + "\"}"; // Asegúrate de cambiar "light" al tipo de dispositivo correcto
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