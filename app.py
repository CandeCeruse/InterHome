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
    print("Connected with result code "+str(rc))
    client.subscribe("device/connected")
    client.subscribe("device/disconnected")
    client.subscribe("temp")
    client.subscribe("device/light/state")

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

        existing_device = next((device for device in devices.values() if device.get('MAC') == device_mac), None)
        if existing_device:
            del devices[existing_device['id']]
            print(f"Device {existing_device['id']} has been removed due to reconnection.")

        new_id = uuid4().hex
        devices[new_id] = {'type': device_type, 'MAC': device_mac, 'name': '', 'state': 'off'}

        print(f"New device connected with ID: {new_id}, Type: {device_type}, MAC: {device_mac}")
    elif topic == "device/disconnected":
        device_info = json.loads(payload)
        device_mac = device_info.get('MAC')

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
        for device_id, device in devices.items():
            if device.get('MAC') == device_MAC:
                device['state'] = device_state
                break

def is_valid_temperature_data(data):
    if not isinstance(data.get('temperature'), (int, float)) or not isinstance(data.get('humidity'), (int, float)):
        return False
    return True

@app.route('/temperature', methods=['GET'])
def temperature():   
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
    light_states = get_light_devices(devices)
    return jsonify(light_states)

def get_temperature_devices(devices):
    temperature_devices = {device_id: device for device_id, device in devices.items() if device['type'] == 'temperature'}
    return temperature_devices

def get_light_devices(devices):
    light_devices = {device_id: device for device_id, device in devices.items() if device['type'] == 'light'}
    return light_devices

def get_device_id_by_mac(devices, mac):
    for device_id, device in devices.items():
        if device.get('MAC') == mac:
            return device_id
    return None

@app.route('/light', methods=['POST'])
def actualizar_estado():
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

@app.route('/update-device-name/<int:device_id>', methods=['POST'])
def update_device_name(device_id):
    new_name = request.form.get('new_name')
    if new_name:
        devices[device_id]['name'] = new_name
        print(f"Device name updated to {new_name} for device with ID: {device_id}")
    return jsonify({'status':'success'})

@app.route("/")
def home():
    devices_list = [{'id': id, 'type': device['type'], 'MAC': device['MAC'], 'name': device['name'], 'state': device['state']} for id, device in devices.items()]
    return render_template("index.html", devices=devices_list)

if __name__ == "__main__":
    client = mqtt.Client("Mqtt-socket-bridge-2021", clean_session=True)   
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, keepalive=60)
    client.loop_start()
    app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=True)
