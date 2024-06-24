# Manual de Usuario para InterHome
![](Logo.jpg)
## Portada
- **Título del manual**: Manual de Usuario para InterHome
- **24/06/2024**
- **Integrantes: Ceruse Candelaria, Piñero Iván, Renolfi Ezequiel, Fioroni Tomás**

## Índice
1. [Introducción](#id1)
2. [Requisitos del Sistema](#id2)
3. [Instalación](#id3)  
  3.1. [Preparación](#id4)  
  3.2. [Instalación del Hardware](#id5)  
  3.3. [Instalación del Software](#id6)  
4. [Configuración](#id7)
5. [Operación](#id8)
6. [Seguridad](#id9)
7. [Apéndices](#id10)


## Introducción<a name="id1"></a>
- **Descripción general del sistema**: Este software puede considerarse una porción de una vivienda inteligente, ya que las funciones que abarca son un subconjunto de un software comercial. El software provee control del encendido y apagado de luces así como el acceso a mediciones de temperatura y humedad del ambiente a partir de una página web, y no soporta características tales como control de electrodomésticos, riego automático, etc. El proyecto funciona de forma independiente a agentes externos y no forma parte de un sistema más grande.

- **Propósito del manual**: Este manual pretende ser una guía para instalar y configurar este proyecto de principio a fin, y ser un punto de partida para la ampliación de InterHome.
- **Audiencia**: Este manual está dirigido a cualquier persona interesada en aprender sobre Sistemas Embebidos y que quiera tomar este proyecto y expandir su funcionalidad.

## Requisitos del Sistema<a name="id2"></a>
- **Hardware necesario**: Listado de dispositivos y componentes necesarios.  
  - Módulo sensores  
    - Chip *ESP8266 NodeMCU*
    - Sensor de Temperatura y Humedad *DHT11*
  - Módulo luces  
    - Chip *ESP8266 NodeMCU*
    - Módulo relé de un canal de 5V.
    - Botón pulsador

- **Software necesario**: El dispositivo de instalación requiere de *Python, Flask, MQTT Mosquitto, Paho MQTT* y *RaspAP* en caso de utilizar una *RaspberryPi*.  
  - Módulo sensores: Código *mqtt_temp_esp8266*
  - Módulo luces: Código *mqtt_lights_esp8266*
- **Requisitos de red**: La red sobre la que funcionará el proyecto debe contar con una conexión de tipo LAN para conectar el módulo central. *RaspAP* cuenta con una modalidad de conexión inalámbrica, pero por el momento resulta inestable, recomendamos investigar esto ya que sería una buena adición al proyecto.

## Instalación<a name="id3"></a>

### Preparación<a name="id4"></a>
- **Consideraciones previas**: Se debe de disponer una conexión estable a red, debido a las múltiples descargas en la instalación de *Software*.

### Instalación del Hardware<a name="id5"></a>
- **Paso a paso para la instalación**:
  - Módulo central: se debe conectar la *RaspberryPi* a una fuente de alimentación y a la red WiFi mediante el cable de red.
  - Módulos de sensores/luces: conexiones detalladas en el esquema.
    - Módulo de sensores: El *ESP8266* se debe conectar a una fuente de alimentación y al pin de datos del sensor *DHT11* mediante el pin 5.
    - Módulo de luces: El *ESP8266* se debe conectar a una fuente de alimentación y al relé mediante el pin 5.
- **Diagramas y fotos**: Los esquemas detallados de conexión de los módulos se encuentran como PDF’s en la carpeta *Placas*, dentro de este repositorio. Además son provistos los archivos en formato *.pdsprj* (Modificables con *Proteus Professional 8*), que habilitan la libre edición de los esquemas del Hardware de los módulos.

### Instalación del Software<a name="id6"></a>
- **Descarga e instalación del software**: Se deben instalar los Software anteriormente mencionados *(Python, Flask, MQTT Mosquitto, Paho-MQTT, RaspAP)*
  - Módulos *ESP8266*: los códigos *mqtt_temp_esp8266* y *mqtt_lights_esp8266* deben ser abiertos mediante un compilador de Arduino como *ArduinoIDE* en una computadora conectada por USB a un chip *ESP8266* para subir los códigos a las mismas.
- **Configuración inicial del software**: Se debe configurar el sistema para que se ejecute el script *levantar_app.sh* junto al inicio del sistema. Para esto se utiliza crontab, que se configura de la siguiente manera;
  ```
  #Abrimos el archivo de configuración de crontab para el usuario
  crontab -e
  #Agregar la siguiente línea al final del código
  @reboot /home/tu_usuario/levantar_app.sh 
  ```

## Configuración<a name="id7"></a>
- *Conexión de dispositivos*: Para acceder a la página web de InterHome el usuario deberá conectarse a la red InterHome (repetida por la Raspberry Pi) y escribir en el buscador:
  ```
  localhost: 5000
  ```

## Operación<a name="id8"></a>
- *Uso diario*: El sistema puede ser utilizado para controlar luces y obtener las medidas de temperatura y humedad donde haya módulos correspondientes instalados.
- *Funciones principales*: El sistema puede ser controlado mediante la interfaz de la página web.

## Seguridad<a name="id9"></a>
- *Recomendaciones de seguridad*: Se recomienda personalizar la contraseña de la red de InterHome con una clave segura.

## Apéndices<a name="id10"></a>
- *Glosario*:  
  - **MQTT:** *Message Queuing Telemetry Transport*.  
