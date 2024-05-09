from flask import Flask, render_template, request, jsonify, redirect, url_for
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from time import sleep
import Freenove_DHT as DHT
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import threading

# Initialize Flask app
app = Flask(__name__)

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Define GPIO pins
DHTPin = 17
LED = 27
LED2 = 5
Motor1 = 16
Motor2 = 20
Motor3 = 21

# Setup GPIO pins
GPIO.setup(DHTPin, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(Motor1, GPIO.OUT)
GPIO.setup(Motor2, GPIO.OUT)
GPIO.setup(Motor3, GPIO.OUT)

# Initialize variables
light_on = False
light_on2 = False
fan_on = False
email_sent = False
light_intensity = 0

# Set default thresholds
default_temp_threshold = 15
default_light_threshold = 400

# Initialize user_info with default values
user_info = {
    "user_id": "Null",
    "name": "Unknown",
    "temp_threshold": 0,
    "humidity_threshold": 0,
    "light_intensity_threshold": 0
}

# MQTT configuration
# mqtt_broker = "192.168.2.32"
mqtt_broker = "192.168.2.38"
mqtt_port = 1883
mqtt_topic_light_intensity = "light_intensity"
mqtt_topic_nuid_dec = "nuid_dec"

# Initialize MQTT client
mqtt_client = mqtt.Client()


# def on_message(client, userdata, message):
#     global light_intensity, email_sent, light_on, user_info, default_temp_threshold, default_light_threshold
#     if message.topic == mqtt_topic_light_intensity:
#         light_intensity = int(message.payload.decode())
#         # Check if user profile thresholds are set
#         if "light_intensity_threshold" in user_info:
#             light_intensity_threshold = int(user_info["light_intensity_threshold"])  # Convert to integer
#             if light_intensity < light_intensity_threshold and not email_sent:
#                 send_light_notification()
#                 email_sent = True
#                 GPIO.output(LED, GPIO.HIGH)
#                 light_on = True
#             elif light_intensity >= light_intensity_threshold:
#                 GPIO.output(LED, GPIO.LOW)
#                 light_on = False
#         else:
#             # Use default light threshold
#             if light_intensity < default_light_threshold and not email_sent:
#                 send_light_notification()
#                 email_sent = True
#                 GPIO.output(LED, GPIO.HIGH)
#                 light_on = True
#             elif light_intensity >= default_light_threshold:
#                 GPIO.output(LED, GPIO.LOW)
#                 light_on = False
#     elif message.topic == mqtt_topic_nuid_dec:
#         try:
#             nuid_dec = message.payload.decode().strip()  # Remove any leading/trailing whitespaces
#             print("Received NUID:", nuid_dec)  # Debugging
#             conn = get_db_connection()
#         
#             user = conn.execute("SELECT * FROM users WHERE REPLACE(UserID, ' ', '') = ?", 
#                                 (nuid_dec.replace(" ", ""),)).fetchone()
#             conn.close()
#             if user:
#                 user_info["user_id"] = nuid_dec
#                 user_info["name"] = user["Name"]
#                 user_info["temp_threshold"] = int(user["Temp_Threshold"])  # Convert to integer
#                 user_info["humidity_threshold"] = int(user["Humidity_Threshold"])  # Convert to integer
#                 user_info["light_intensity_threshold"] = int(user["Light_Intensity_Threshold"])  # Convert to integer
#                 print("User info retrieved successfully:", user_info)  # Debugging
#                 # Send email
#                 send_rfid_notification(user_info["name"])
#                 # Add debug message for threshold reset
#                 print("Thresholds reset to user's preferences:", user_info["light_intensity_threshold"])
#             else:
#                 print("No user found with the provided NUID:", nuid_dec)  # Debugging
#         except Exception as e:
#             print("Error:", e)
#             return
# 
#         # Update default thresholds only if user profile information is not available
#         if "light_intensity_threshold" not in user_info:
#             default_temp_threshold = 15
#             default_light_threshold = 400
#             print("Default temp threshold set:", default_temp_threshold)
#             print("Default light threshold set:", default_light_threshold)

def on_message(client, userdata, message):
    global light_intensity, email_sent, light_on, user_info
    if message.topic == mqtt_topic_light_intensity:
        light_intensity = int(message.payload.decode())
        if light_intensity < int(user_info["light_intensity_threshold"]) and not email_sent:
            send_light_notification()
            email_sent = True
            GPIO.output(LED, GPIO.HIGH)
            light_on = True
        elif light_intensity >= int(user_info["light_intensity_threshold"]):
            GPIO.output(LED, GPIO.LOW)
            light_on = False
    elif message.topic == mqtt_topic_nuid_dec:
        try:
            nuid_dec = message.payload.decode().strip()  # Remove any leading/trailing whitespaces
            print("Received NUID:", nuid_dec)  # Debugging
            conn = get_db_connection()
        
            user = conn.execute("SELECT * FROM users WHERE REPLACE(UserID, ' ', '') = ?", 
                                (nuid_dec.replace(" ", ""),)).fetchone()
            conn.close()
            if user:
                user_info["user_id"] = nuid_dec
                user_info["name"] = user["Name"]
                user_info["temp_threshold"] = user["Temp_Threshold"]
                user_info["humidity_threshold"] = user["Humidity_Threshold"]
                user_info["light_intensity_threshold"] = user["Light_Intensity_Threshold"]
                print("User info retrieved successfully:", user_info)  # Debugging
                 # Send email
                send_rfid_notification(user_info["name"])  

            else:
                print("No user found with the provided NUID:", nuid_dec)  # Debugging
        except Exception as e:
            print("Error:", e)
        


# Set MQTT client callbacks and connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port)
mqtt_client.subscribe([(mqtt_topic_light_intensity, 0), (mqtt_topic_nuid_dec, 0)])

# Start the MQTT client loop in a background thread
mqtt_thread = threading.Thread(target=mqtt_client.loop_start)
mqtt_thread.start()

def get_db_connection():
    conn = sqlite3.connect("IoTHome.db")
    conn.row_factory = sqlite3.Row  # Allows accessing data by column name
    return conn

@app.route('/update_profile', methods=['POST'])
def update_profile():
    temperature_threshold = request.form['temperature']
    humidity_threshold = request.form['humidity']
    light_intensity_threshold = request.form['light_intensity']

    conn = get_db_connection()
    conn.execute("UPDATE users SET Temp_Threshold=?, Humidity_Threshold=?, Light_Intensity_Threshold=? WHERE UserID=?",
                 (temperature_threshold, humidity_threshold, light_intensity_threshold, user_info["user_id"]))
    conn.commit()
    conn.close()

    # Update user_info with new thresholds
    user_info["temp_threshold"] = temperature_threshold
    user_info["humidity_threshold"] = humidity_threshold
    user_info["light_intensity_threshold"] = light_intensity_threshold

    # Debug message
    print("User info updated:", user_info)
    
    # Redirect to index route with updated user_info
    return redirect(url_for('index'))



# Function to toggle the light
def toggle_light():
    global light_on2
    if not light_on2:
        GPIO.output(LED2, GPIO.HIGH)
        light_on2 = True
    else:
        GPIO.output(LED2, GPIO.LOW)
        light_on2 = False

# Function to toggle the fan
def toggle_fan():
    global fan_on
    if not fan_on:
        GPIO.output(Motor1, GPIO.HIGH)
        GPIO.output(Motor2, GPIO.LOW)
        GPIO.output(Motor3, GPIO.HIGH)
        fan_on = True
    else:
        GPIO.output(Motor1, GPIO.LOW)
        fan_on = False

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

# Function to send email notification for temperature
def send_email_notification(temp):
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Temperature Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"The current temperature is {temp}. Would you like to turn on the fan?"
    html = f"""\
        <html>
        <head>
            <style>
            .container {{
                padding: 20px;
                font-family: Arial, sans-serif;
                text-align: center; /* Center-align the content */
            }}
            .message {{
                margin-bottom: 20px;
            }}
            .a {{
                display: inline-block; /* Display the buttons in a block */
            }}
            .a {{
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                margin: 5px; /* Add margin between buttons */
                display: inline-block; /* Display buttons in a line */
            }}
            </style>
        </head>
        <body>
            <div class="container">
            <div class="message">
                <p>The current temperature is {temp}. Would you like to turn on the fan?</p>
            </div>
            <div class="buttons">
                  <p><a href="http://127.0.0.1:5000/confirm_fan?choice=yes" class="email-link">Yes, turn on the fan</a></p>
                  <p><a href="http://127.0.0.1:5000/confirm_fan?choice=no" class="email-link">No, keep it off</a></p>
            </div>
            </div>
        </body>
        </html>
        """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP("smtp.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to send email notification for light
def send_light_notification():
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Light Alert"

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    light_intensity_message = f"Light Intensity: {light_intensity}"

    body = f"The Light is ON at {current_time} time. {light_intensity_message}"
    message.attach(MIMEText(body, "plain"))


    try:
        with smtplib.SMTP("smtp.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email notification sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        
        
def send_rfid_notification(user_name):
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"

    message = MIMEMultipart("alternative")
    message["Subject"] = "RFID Tag Notification"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"User {user_name} entered at {datetime.datetime.now()}"
    html = f"""\
        <html>
        <head></head>
        <body>
            <p>User {user_name} entered at {datetime.datetime.now()}</p>
        </body>
        </html>
        """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP("smtp.outlook.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("RFID tag notification sent successfully!")
    except Exception as e:
        print(f"Failed to send RFID tag notification: {e}")


@app.route('/')
def index():
    humidity, temperature = read_dht_sensor()
    email_status = "Email has been sent" if email_sent else None

    # Pass user information from MQTT to the template
    return render_template(
        'index.html',
        user_id=user_info["user_id"],
        name=user_info["name"],
        temp_threshold=user_info["temp_threshold"],
        humidity_threshold=user_info["humidity_threshold"],
        light_intensity_threshold=user_info["light_intensity_threshold"],
        light_status2=light_on2,
        fan_status=fan_on,
        temperature=temperature,
        humidity=humidity,
        light_intensity=light_intensity,
        light_status=light_on,
        email_status=email_status
    )


@app.route('/toggle_fan')
def toggle_fan_route():
    toggle_fan()
    return 'OK'


@app.route('/sensor_data')
def sensor_data():
    global light_on, email_sent
    
    # Read sensor data
    humidity, temperature = read_dht_sensor()
    
    if temperature is not None:
        # Check temperature threshold
        if "temp_threshold" in user_info:
            if temperature > float(user_info["temp_threshold"]):
                # Send email notification if not already sent
                if not email_sent:
                    send_email_notification(temperature)
                    email_sent = True
            else:
                # Turn off email_sent flag if temperature is below threshold
                email_sent = False
        else:
            # Use default temperature threshold
            if temperature > default_temp_threshold:
                if not email_sent:
                    send_email_notification(temperature)
                    email_sent = True
            else:
                email_sent = False
            
    # Check light intensity threshold
    if "light_intensity_threshold" in user_info:
        if light_intensity < int(user_info["light_intensity_threshold"]):
            # Turn on the light if it's off
            if not light_on:
                GPIO.output(LED, GPIO.HIGH)
                light_on = True
        else:
            # Turn off the light if it's on
            if light_on:
                GPIO.output(LED, GPIO.LOW)
                light_on = False
    else:
        # Use default light intensity threshold
        if light_intensity < default_light_threshold:
            if not light_on:
                GPIO.output(LED, GPIO.HIGH)
                light_on = True
        else:
            if light_on:
                GPIO.output(LED, GPIO.LOW)
                light_on = False
    
    return jsonify({'temperature': temperature, 'humidity': humidity, 'light_intensity': light_intensity})

@app.route('/light_status')
def light_status():
    return jsonify({'light_intensity': light_intensity, 'light_status': 'ON' if light_on else 'OFF', 'email_status': 'SENT' if email_sent else 'NOT SENT'})

@app.route('/confirm_fan', methods=['GET'])
def confirm_fan():
    choice = request.args.get('choice')
    if choice == 'yes':
        toggle_fan_on()
    elif choice == 'no':
        toggle_fan_off()
    return redirect(url_for('index'))

def toggle_fan_on():
    global fan_on
    if not fan_on:
        toggle_fan()
        fan_on = True
        fan_status = "on"  

def toggle_fan_off():
    global fan_on
    if fan_on:
        toggle_fan()
        fan_on = False
        fan_status = "off"  # Update status
        
@app.route('/toggle')
def toggle():
    toggle_light()
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
