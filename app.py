from flask import Flask, jsonify, request, render_template
#from flask_mqtt import Mqtt
from flask_socketio import SocketIO, emit
import json
import paho.mqtt.client as mqtt
#from modules.pruebamqtt import enviar_mensaje

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "secret!"

# Configuración de CORS para permitir solicitudes desde el dominio del cliente
socketio = SocketIO(app)

#Variables globales
devices = {}
last_temperature_data = None

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("device/connected")
    client.subscribe("device/disconnected")
    client.subscribe("temp")

def on_message(client, userdata, message):
    global last_temperature_data
    topic = message.topic
    payload = message.payload.decode()
    print(f"Received message on topic {topic}: {payload}")
    global devices
    if topic == "device/connected":
        device_info = json.loads(payload)
        device_type = device_info.get('type')
        device_mac = device_info.get('MAC')
        
        device_id = len(devices) + 1 # Asigna un ID basado en el número de dispositivos conectados
        devices[device_id] = {'type': device_type, 'MAC': device_mac}
        print(f"Device ID: {device_id}, Type: {device_type}, Device MAC: {device_mac}") # Muestra el ID y el tipo de dispositivo
    elif topic == "device/disconnected":
        print("Device disconnected")
        device_info = json.loads(payload)
        device_mac = device_info.get('MAC')
        print(f"Device MAC: {device_mac}")
        # Eliminar el dispositivo de la lista de dispositivos conectados
        
        for device_id, device in devices.items():
            if device.get('MAC') == device_mac:
                del devices[device_id]
                break
    elif topic == 'temp':
        try:
            temperature_data = json.loads(payload)
            if not is_valid_temperature_data(temperature_data):
                print("Datos de temperatura no válidos")
                return
            last_temperature_data = temperature_data
        except ValueError as e:
            print(f"Error al procesar los datos de temperatura: {e}")
            
    temperature_devices = get_temperature_devices(devices)


def is_valid_temperature_data(data):
    if not isinstance(data.get('temperature'), (int, float)) or not isinstance(data.get('humidity'), (int, float)):
        return False
    return True


@app.route('/temperature', methods=['GET'])
def temperature():   
    global last_temperature_data
    if last_temperature_data is None or not is_valid_temperature_data(last_temperature_data):
        return jsonify({"error": "No hay datos válidos disponibles"}), 404
    else:
        # Encuentra el ID del dispositivo basado en la MAC
        device_mac = last_temperature_data.get('MAC')
        device_id = get_device_id_by_mac(devices, device_mac)
        # Agrega el ID del dispositivo al objeto JSON
        if device_id is not None:
            last_temperature_data['device_id'] = device_id
        #print(last_temperature_data)
        return jsonify(last_temperature_data)
    
def get_temperature_devices(devices):
    # Filtra el diccionario para obtener solo los dispositivos de tipo 'temperatura'
    temperature_devices = {device_id: device for device_id, device in devices.items() if device['type'] == 'temperature'}
    return temperature_devices

def get_device_id_by_mac(devices, mac):
    for device_id, device in devices.items():
        if device.get('MAC') == mac:
            return device_id
    return None

# Ruta para manejar la solicitud POST
@app.route('/light', methods=['POST'])
def actualizar_estado():
    data = request.json # Obtiene los datos JSON enviados en el cuerpo de la solicitud
    topic = data.get('topic', 'light')
    id = data.get('id', '')
    state = data.get('state', 'OFF')
    # Buscar el dispositivo por ID y obtener su MAC
    device_mac = None
    for device_id, device_info in devices.items():
        if str(device_id) == id:
            device_mac = device_info.get('MAC')
            break
    if device_mac:
        # Construir el tema específico para el dispositivo
        device_topic = f"device/{topic}/{device_mac}"
        publish_result = client.publish(device_topic, state)
        print(f"topic: {device_topic}, id: {id}, state: {state}")
        return jsonify({'code': publish_result[0]})
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route("/")
def home():
    devices_list = [{'id': id, 'type': device['type'], 'MAC': device['MAC']} for id, device in devices.items()]
    return render_template("index.html", devices=devices_list)

if __name__ == "__main__":
    client = mqtt.Client("Mqtt-socket-bridge-2021", clean_session=True)   
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, keepalive=60)
    client.loop_start()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
