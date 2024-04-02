from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
from time import sleep
import Freenove_DHT as DHT
# email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

if GPIO.getmode() is None:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

LED = 27
# FAN = 22
GPIO.setup(LED, GPIO.OUT)
light_on = False
fan_on = False
email_sent = False

DHTPin = 17

def toggle_light():
    global light_on
    if not light_on:
        GPIO.output(LED, GPIO.HIGH)
        light_on = True
    else:
        GPIO.output(LED, GPIO.LOW)
        light_on = False
            
def read_dht_sensor():
    dht = DHT.DHT(DHTPin)
    counts = 0
    for i in range(0, 15):
        chk = dht.readDHT11()
        if chk is dht.DHTLIB_OK:
            return dht.humidity, dht.temperature
        sleep(0.1)
    return None, None

def toggle_fan():
    global fan_on
    if not fan_on:
        GPIO.output(FAN, GPIO.HIGH)
        fan_on = True
    else:
        GPIO.output(FAN, GPIO.LOW)
        fan_on = False

@app.route('/')
def index():
    humidity, temperature = read_dht_sensor()
    return render_template('index.html', light_status=light_on, temperature=temperature, humidity=humidity)

@app.route('/toggle')
def toggle():
    toggle_light()
    return 'OK'

@app.route('/sensor_data')
def sensor_data():
    global email_sent
    humidity, temperature = read_dht_sensor()
    if temperature is not None and temperature > 22 and not email_sent:
        send_email(temperature)
        email_sent = True
    return jsonify({'temperature': temperature, 'humidity': humidity})


@app.route('/fan_toggle')
def fan_toggle():
    toggle_fan()
    return 'fan toggle is OK'

@app.route('/confirm_fan', methods=['GET'])
def confirm_fan():
    choice = request.args.get('choice')
    if choice == 'yes':
        fan_toggle()
        pass
    elif choice == 'no':
        # Code to keep the fan off
        pass
    return "Fan status updated successfully."

def send_email(temp):
    # Email configuration
    sender_email = "iot-master-o@outlook.com"
    receiver_email = "iot-master-o@outlook.com"
    password = "iot4life"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Temperature Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

   
    # Email content
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
              <p><a href="http://127.0.0.1:5000/confirm_fan?choice=yes">Yes, turn on the fan</a></p>
              <p><a href="http://127.0.0.1:5000/confirm_fan?choice=no">No, keep it off</a></p>
        </div>
        </div>
    </body>
    </html>
    """


    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # Sending email
    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
