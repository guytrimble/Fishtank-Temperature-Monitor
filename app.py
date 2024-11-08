from flask import Flask, render_template
import paho.mqtt.client as paho
import os
from dotenv import load_dotenv
load_dotenv()

temperature = -1
username = os.getenv('MQTT_FISHTANK_USER')
password = os.getenv('MQTT_FISHTANK_PASS')
broker_url = os.getenv('MQTT_FISHTANK_URL')

# Tells Flask location of current file for creating the website
app = Flask(__name__)

#Defines callback for connect. If no errors subscribes to topic.
#Subscribes to topic and qos = 2 means each message is delivered exactly once
def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))
    if rc == 0:
        print("Connected succesfully")
        client.subscribe('esp8266_temperature', qos=2)
    else:
        print("Connection failed %d:" % (rc))

#Defines callback for subscribe. Print subscribed to topic.
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + str(granted_qos))

def on_message(client, userdata, msg):
    #creates global variable called temperature for the temp from MQTT messages
    global temperature
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    temperature = float(msg.payload)

#creates new MQTT client
client = paho.Client()

#Sets callbacks to functions created earlier
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

def connect_to_mqtt():
    try:
        #Sets username and password for MQTT credentials
        client.username_pw_set(username, password)

        #TLS Enabled
        client.tls_set()

        #Connects in background to MQTT broker with info in parameters, url, port, keep alive
        client.connect_async(broker_url, 8883, 60, )
        
        #Start loop to receive messages
        client.loop_start()
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")

with app.app_context():
    connect_to_mqtt()

@app.teardown_appcontext
def end_connection_to_mqtt(error):
    client.loop_stop()
    client.disconnect()
    if error:
        print(error)

# Defines what is displayed on the home page as what is in index.html
@app.route('/')
def index():
    return render_template('index.html', temperature_for_web = temperature)

# If the script is being run directly and not imported, it starts the Flask app server
if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=False)
