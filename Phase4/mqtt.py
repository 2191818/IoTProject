import paho.mqtt.client as mqtt
import threading
from pins import initialize_gpio
import time
from RPi import GPIO
from email_noti import send_light_notification

# Shared data dictionary
mqtt_data = {
    "light_intensity": None,
    "nuid_dec": None,
}
 
# MQTT configuration
mqtt_broker = "192.168.2.91"
mqtt_port = 1883
mqtt_topic_light = "light_intensity"
mqtt_topic_rfid = 'nuid_dec'

# Initialize MQTT client
mqtt_client = mqtt.Client()

# Flags 
email_sent = False
light_on = False

# MQTT message callback
def on_message(client, userdata, message):
    global mqtt_data, email_sent, light_on
    try:
        topic = message.topic
        payload = message.payload.decode()

        if topic == mqtt_topic_light:
            mqtt_data["light_intensity"] = int(payload)
        elif topic == mqtt_topic_rfid:
            mqtt_data["rfid_nuid"] = payload
    
        if mqtt_data < 400 and not email_sent:
            send_light_notification(mqtt_data)
            email_sent = True
            GPIO.output(LED, GPIO.HIGH)
            light_on = True
        elif light_intensity >= 400:
            GPIO.output(LED, GPIO.LOW)
            light_on = False

    except ValueError:
        print("Error: Invalid MQTT message payload")
        return


# Connect to MQTT broker and subscribe to the light topic
def mqtt_loop():
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_broker, mqtt_port)
    mqtt_client.subscribe([(mqtt_topic_light, 0), (mqtt_topic_rfid, 0)]) 
    mqtt_client.loop_forever()  # Keep the MQTT client running

# Start MQTT client in a separate thread
threading.Thread(target=mqtt_loop).start()