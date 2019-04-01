import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import ssl
import time


config = {}
try:
       with open('config.json') as json_data:
                   config = json.load(json_data)
except Exception as e:
            print("Config load failed")
            exit(1)

gpio = [
        [14,"bin_out_heating","ON","OFF"],
        [15,"bin_out_light_gate","ON","OFF"],
        [18,"bin_out_light_door","ON","OFF"],
        [23,"bin_out_light_court","ON","OFF"]
]
pub_topic = 'home/outputs/'



def on_connect(client, userdata, rc, *extra_params):
    #print('Connected with result code ' + str(rc))
    for g2 in gpio:
        #print ("Subscribe",pub_topic + g2[1] + '/set')
        client.subscribe(pub_topic + g2[1] + '/set')
        client.publish(pub_topic + g2[1],g2[3],0,0)


def on_message(client, userdata, msg):
    #print ('Topic: ' + msg.topic + ' Message: ' + str(msg.payload.decode('ascii')))
    data = msg.topic.split("/")
    #time.sleep(1)
    client.publish(pub_topic + data[2],set_gpio_status(ch[data[2]],msg.payload.decode('ascii')),2,True)


def set_gpio_status(pin, status):
    #print ('set: status: ' + status)
    #if (status == "true") or (int(status) == 1) or (status is "ON"):
    #if status == "ON" or  status == "1" or status == "true":
    if ((status == "1") or (status == "ON") or (status == "true")):
        GPIO.output(pin, GPIO.HIGH)
        return ch_on[pin]
    else:
        GPIO.output(pin, GPIO.LOW)
        return ch_off[pin]


GPIO.setmode(GPIO.BCM)

ch = dict()
ch_on = dict()
ch_off = dict()
for g2 in gpio:
    #print ("Gpio setup",  g2[0])
    GPIO.setup(g2[0], GPIO.OUT, initial=GPIO.LOW)
    ch[g2[1]] = g2[0]	
    ch_on[g2[0]] = g2[2]	
    ch_off[g2[0]] = g2[3]	



client = mqtt.Client(client_id='RPI-MQTT-OUT'
        '', clean_session=True, userdata=None)
client.tls_set(ca_certs=None, certfile=None,
                keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.tls_insecure_set(False)
client.username_pw_set(config['username'], password=config['password'])
client.on_connect = on_connect
client.on_message = on_message
client.connect(config['mqtt_host'], port=config['mqtt_port'], keepalive=120)


try:
    client.loop_forever()
except KeyboardInterrupt:
    GPIO.cleanup()
