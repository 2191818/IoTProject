import RPi.GPIO as GPIO
from time import sleep
import os

# Function to initialize GPIO
def initialize_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    # Define GPIO pins
    DHTPin = 17
    LED = 27
    LED2 = 5
    Motor1 = 6
    Motor2 = 13
    Motor3 = 19

    GPIO.setup(DHTPin, GPIO.OUT)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.setup(LED2, GPIO.OUT)
    GPIO.setup(Motor1, GPIO.OUT)
    GPIO.setup(Motor2, GPIO.OUT)
    GPIO.setup(Motor3, GPIO.OUT)

    return {
        "DHT": DHTPin,
        "led": LED,
        "led2": LED2,
        "motor1": Motor1,
        "motor2": Motor2,
        "motor3": Motor3,
    }

# Function to check GPIO pin status
def check_pin_status(pins):
    status = {}

    for pin_name, pin_number in pins.items():
        try:
            # Set to input with pull-down resistor
            GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            # Read the pin; if it's high, it's probably connected
            pin_connected = GPIO.input(pin_number)
            status[pin_name] = "connected" if pin_connected else "not Connected"
        except Exception as e:  
            status[pin_name] = f"Error: {e}"

    return status


# Function to play audio indicating the status of each component
def play_audio_based_on_status(status):
    base_audio_path = "static/audio"

    for pin_name, connection_status in status.items():
        audio_file_name = f"{pin_name}_{connection_status.replace(' ', '_')}.mp3"
        audio_file_path = f"{base_audio_path}/{audio_file_name}"

        # Check if the audio file exists before playing
        if os.path.isfile(audio_file_path):
            os.system(f"omxplayer {audio_file_path}")
        else:
            print(f"Audio file not found: {audio_file_path}")



# Function to toggle light
def toggle_light(led_pin, light_status):
    if not light_status:
        GPIO.output(led_pin, GPIO.HIGH)
        light_status = True
    else:
        GPIO.output(led_pin, GPIO.LOW)
        light_status = False
    return light_status

# Function to toggle fan
def toggle_fan(motor_pins, fan_status):
    if not fan_status:
        GPIO.output(motor_pins[0], GPIO.HIGH)
        GPIO.output(motor_pins[1], GPIO.LOW)
        GPIO.output(motor_pins[2], GPIO.HIGH)
        fan_status = True
    else:
        GPIO.output(motor_pins[0], GPIO.LOW)
        fan_status = False
    return fan_status