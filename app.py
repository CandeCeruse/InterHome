from flask import Flask, jsonify, request, render_template
import json
import paho.mqtt.client as mqtt
from uuid import uuid4

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = "secret!"

# Variables globales para almacenar información sobre los dispositivos conectados 
devices = {}
last_temperature_data = None

def on_connect(client, userdata, flags, rc):
    """
    Callback que se ejecuta cuando el cliente se conecta al broker MQTT.

    Args:
        client: La instancia del cliente MQTT.
        userdata: Los datos definidos por el usuario.
        flags: Banderas relacionadas con la conexión.
        rc: Código de resultado de la conexión.
    """
    print("Connected with result code "+str(rc))
    client.subscribe("device/connected")
    client.subscribe("device/disconnected")
    client.subscribe("temp")
    client.subscribe("device/light/state")

def on_message(client, userdata, message):
    """
    Callback que se ejecuta cuando se recibe un mensaje desde el broker MQTT.

    Args:
        client: La instancia del cliente MQTT.
        userdata: Los datos definidos por el usuario.
        message: El mensaje recibido del broker MQTT.
    """
    global last_temperature_data
    topic = message.topic
    payload = message.payload.decode()
    print(f"Received message on topic {topic}: {payload}")
    global devices

    if topic == "device/connected":
        device_info = json.loads(payload)
        device_type = device_info.get('type')
        device_mac = device_info.get('MAC')

        # Verifica si el dispositivo ya está conectado
        existing_device = next((device for device in devices.values() if device.get('MAC') == device_mac), None)
        if existing_device:
            del devices[existing_device['id']]
            print(f"Device {existing_device['id']} has been removed due to reconnection.")

        # Asigna un nuevo ID y guarda la información del dispositivo
        new_id = uuid4().hex
        devices[new_id] = {'type': device_type, 'MAC': device_mac, 'name': '', 'state': 'off'}
        print(f"New device connected with ID: {new_id}, Type: {device_type}, MAC: {device_mac}")

    elif topic == "device/disconnected":
        device_info = json.loads(payload)
        device_mac = device_info.get('MAC')

        # Elimina el dispositivo desconectado
        for device_id, device in devices.items():
            if device.get('MAC') == device_mac:
                del devices[device_id]
                print(f"Device {device_id} has been disconnected.")
                break

    elif topic == 'temp':
        try:
            temperature_data = json.loads(payload)
            if not is_valid_temperature_data(temperature_data):
                print("Invalid temperature data")
                return
            last_temperature_data = temperature_data
        except ValueError as e:
            print(f"Error processing temperature data: {e}")

    elif topic == 'device/light/state':
        state_data = json.loads(payload)
        device_state = state_data.get('state')
        device_MAC = state_data.get('MAC')
        
        # Actualiza el estado del dispositivo
        for device_id, device in devices.items():
            if device.get('MAC') == device_MAC:
                device['state'] = device_state
                break

def is_valid_temperature_data(data):
    """
    Valida si los datos de temperatura son correctos.

    Args:
        data: Un diccionario con los datos de temperatura.

    Returns:
        bool: True si los datos son válidos, False en caso contrario.
    """
    if not isinstance(data.get('temperature'), (int, float)) or not isinstance(data.get('humidity'), (int, float)):
        return False
    return True

@app.route('/temperature', methods=['GET'])
def temperature():
    """
    Ruta para obtener los datos de temperatura más recientes.

    Returns:
        Response: Una respuesta JSON con los datos de temperatura.
    """   
    global last_temperature_data
    if last_temperature_data is None or not is_valid_temperature_data(last_temperature_data):
        return jsonify({"error": "No valid data available"}), 404
    else:
        device_mac = last_temperature_data.get('MAC')
        device_id = get_device_id_by_mac(devices, device_mac)
        if device_id is not None:
            last_temperature_data['device_id'] = device_id
        return jsonify(last_temperature_data)

@app.route('/state/light', methods=['GET'])
def state_light():
    """
    Ruta para obtener el estado de los dispositivos de luz.

    Returns:
        Response: Una respuesta JSON con los estados de los dispositivos de luz.
    """
    light_states = get_light_devices(devices)
    return jsonify(light_states)

def get_temperature_devices(devices):
    """
    Obtiene una lista de dispositivos de temperatura.

    Args:
        devices: Un diccionario con todos los dispositivos conectados.

    Returns:
        dict: Un diccionario con los dispositivos de temperatura.
    """
    temperature_devices = {device_id: device for device_id, device in devices.items() if device['type'] == 'temperature'}
    return temperature_devices

def get_light_devices(devices):
    """
    Obtiene una lista de dispositivos de luz.

    Args:
        devices: Un diccionario con todos los dispositivos conectados.

    Returns:
        dict: Un diccionario con los dispositivos de luz.
    """
    light_devices = {device_id: device for device_id, device in devices.items() if device['type'] == 'light'}
    return light_devices

def get_device_id_by_mac(devices, mac):
    """
    Obtiene el ID de un dispositivo a partir de su dirección MAC.

    Args:
        devices: Un diccionario con todos los dispositivos conectados.
        mac: La dirección MAC del dispositivo.

    Returns:
        str or None: El ID del dispositivo si se encuentra, None en caso contrario.
    """
    for device_id, device in devices.items():
        if device.get('MAC') == mac:
            return device_id
    return None

@app.route('/light', methods=['POST'])
def actualizar_estado():
    """
    Actualiza el estado de un dispositivo de luz.

    Returns:
        Response: Una respuesta JSON con el resultado de la publicación del estado.
    """
    data = request.json
    topic = data.get('topic', 'light') 
    id = data.get('id', '')
    state = data.get('state', 'OFF')
    device_mac = None

    for device_id, device_info in devices.items():
        if str(device_id) == id:
            device_mac = device_info.get('MAC')
            break

    if device_mac:
        device_topic = f"device/{topic}/{device_mac}"
        publish_result = client.publish(device_topic, state)
        print(f"topic: {device_topic}, id: {id}, state: {state}")
        return jsonify({'code': publish_result[0]})
    else:
        return jsonify({'error': 'Device not found'}), 404

@app.route('/update-device-name', methods=['POST'])
def update_device_name():
    """
    Actualiza el nombre de un dispositivo.

    Returns:
        Response: Una respuesta JSON indicando el éxito de la operación.
    """
    data = request.json
    new_name = data.get('name', '')
    device_id = data.get('id', '')
    if new_name:
        # Accede al dispositivo por su ID en el diccionario devices
        if str(device_id) in devices:
            # Actualiza el nombre del dispositivo en el diccionario devices
            devices[str(device_id)]['name'] = new_name
            print(f"Device name updated to {new_name} for device with ID: {device_id}")
        else:
            print(f"No device found with ID: {device_id}")
    return jsonify({'status':'success'})

@app.route('/set/label', methods=['GET'])
def setLabel():
    """
    Obtiene una lista de dispositivos con sus etiquetas (ID y nombre).

    Returns:
        Response: Una respuesta JSON con los IDs y nombres de los dispositivos.
    """
    # Construye una lista de objetos con el ID y el nombre de cada dispositivo
    device_labels = [{"id": id, "name": device['name']} for id, device in devices.items()]
    return jsonify(device_labels)

@app.route("/")
def home():
    """
    Ruta principal que renderiza la página principal con la lista de dispositivos.

    Returns:
        Response: Renderiza la plantilla 'index.html' con los dispositivos.
    """
    devices_list = [{'id': id, 'type': device['type'], 'MAC': device['MAC'], 'name': device['name'], 'state': device['state']} for id, device in devices.items()]
    return render_template("index.html", devices=devices_list)

if __name__ == "__main__":
    # Configuración y conexión del cliente MQTT
    client = mqtt.Client("Mqtt-socket-bridge-2021", clean_session=True)   
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, keepalive=60)
    client.loop_start()
    # Inicia la aplicación Flask
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)
