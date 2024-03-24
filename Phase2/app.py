from flask import Flask, render_template
import RPi.GPIO as GPIO
from time import sleep

app = Flask(__name__)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED = 27
#BUTTON = 12

GPIO.setup(LED, GPIO.OUT)
#GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

light_on = False
temperature_reading = 25  # Example temperature reading

def toggle_light():
    global light_on
    if not light_on:
        GPIO.output(LED, GPIO.HIGH)
        light_on = True
    else:
        GPIO.output(LED, GPIO.LOW)
        light_on = False

@app.route('/')
def index():
    return render_template('index.html', light_status=light_on, temperature=temperature_reading)

@app.route('/toggle')
def toggle():
    toggle_light()
    return 'OK'

#def button_callback(channel):
#   toggle_light()
#   app.logger.info("Button pressed, light status changed.")

#GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=300)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
