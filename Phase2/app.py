from flask import Flask, render_template, jsonify, request, redirect, url_for
import RPi.GPIO as GPIO
from time import sleep
import Freenove_DHT as DHT
# Email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

if GPIO.getmode() is None:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

LED = 27
GPIO.setup(LED, GPIO.OUT)
light_on = False
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
    if temperature is not None and temperature > 15 and not email_sent:
        send_email(temperature)
        email_sent = True
    return jsonify({'temperature': temperature, 'humidity': humidity})

@app.route('/confirm_fan', methods=['GET'])
def confirm_fan():
    choice = request.args.get('choice')
    if choice == 'yes':
        toggle_light()
        return redirect(url_for('index'))
    return "Fan status updated successfully."

def send_email(temp):
    # Email configuration
    sender_email = "kingdaxter360@gmail.com"
    receiver_email = "kingdaxter360@gmail.com"
    password = "iwxy ynue zzni xkzq"

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
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
