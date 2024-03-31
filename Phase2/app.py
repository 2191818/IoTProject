from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
from time import sleep
import Freenove_DHT as DHT

app = Flask(__name__)

if GPIO.getmode() is None:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

LED = 27
GPIO.setup(LED, GPIO.OUT)
light_on = False

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
    humidity, temperature = read_dht_sensor()
    return jsonify({'temperature': temperature, 'humidity': humidity})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
