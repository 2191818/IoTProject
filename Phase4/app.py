from flask import Flask, render_template, jsonify, request, redirect, url_for
import RPi.GPIO as GPIO
from pins import initialize_gpio, toggle_light, toggle_fan, check_pin_status, play_audio_based_on_status
from email_noti import send_email_notification, send_light_notification
import Freenove_DHT as DHT
import paho.mqtt.client as mqtt
import threading
import sqlite3

# Initialize Flask app
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("IoTHome.db")
    conn.row_factory = sqlite3.Row  # Allows accessing data by column name
    return conn

# Initialize GPIO and play audio at startup
pins = initialize_gpio()
status = check_pin_status(pins)
play_audio_based_on_status(status)

# Initialize global variables
light_on = False
light_on2 = False
fan_on = False
email_sent = False

# Store the latest light intensity value
light_intensity = {"value": None}
 
# MQTT configuration
mqtt_broker = "192.168.2.91"
mqtt_port = 1883
mqtt_topic = "light_intensity"

# Initialize MQTT client
mqtt_client = mqtt.Client()

# MQTT message callback
def on_message(client, userdata, message):
    global light_intensity, email_sent, light_on
    try:
         light_intensity["value"] = int(message.payload.decode())
    except ValueError:
        print("Error: Invalid MQTT message payload")
        return

    if light_intensity < 400 and not email_sent:
        send_light_notification(light_intensity)
        email_sent = True
        GPIO.output(LED, GPIO.HIGH)
        light_on = True
    elif light_intensity >= 400:
        GPIO.output(LED, GPIO.LOW)
        light_on = False

# Connect to MQTT broker and subscribe to the light topic
def mqtt_loop():
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port)
    mqtt_client.subscribe(light_topic)
    mqtt_client.loop_forever()  # Keep the MQTT client running

# Start the MQTT client in a background thread
mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

# Function to read DHT sensor
def read_dht_sensor():
    dht = DHT.DHT(DHTPin)
    counts = 0
    for i in range(0, 15):
        chk = dht.readDHT11()
        if chk is dht.DHTLIB_OK:
            return dht.humidity, dht.temperature
        sleep(0.1)
    return None, None

# Flask routes
@app.route('/')
def index():
    user_id = "0"
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE UserID = ?", (user_id,)).fetchone()
    
    if not user:
        return "User not found", 404
    
    # Fetch the role from the auth table
    role = conn.execute("SELECT role FROM auth WHERE id = ?", (user["role_id"],)).fetchone()
    
    conn.close()

    humidity, temperature = read_dht_sensor()
    email_status = "Email has been sent" if email_sent else None
    current_intensity = light_intensity["value"]
    return render_template(
        'index.html',
        user=user["UserID"],   
        name=user["Name"],  
        temp_threshold=user["Temp. Threshold"],  
        humidity_threshold=user["Humidity Threshold"],  
        light_intensity_threshold=user["Light intensity Threshold"],
        light_status2=light_on2,
        fan_status=fan_on,
        temperature=temperature,
        humidity=humidity,
        light_intensity=current_intensity,
        light_status=light_on,
        email_status=email_status
    )

@app.route('/toggle')
def toggle():
    global light_on2
    light_on2 = toggle_light(LED2, light_on2)
    return 'OK'

@app.route('/toggle_fan')
def toggle_fan_route():
    global fan_on
    fan_on = toggle_fan([Motor1, Motor2, Motor3], fan_on)
    return 'OK'

@app.route('/sensor_data')
def sensor_data():
    global email_sent, light_on
    humidity, temperature = read_dht_sensor()
    
    if temperature is not None:
        if temperature > 15 and not email_sent:
            send_email_notification(temperature)
            email_sent = True
    
    return jsonify({
        'temperature': temperature,
        'humidity': humidity,
        'light_intensity': light_intensity,
        'light_status': 'ON' if light_on else 'OFF',
        'email_status': 'SENT' if email_sent else 'NOT SENT'
    })

@app.route('/confirm_fan', methods=['GET'])
def confirm_fan():
    choice = request.args.get('choice')
    if choice == 'yes':
        toggle_fan_route()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
