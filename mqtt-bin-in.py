#!/usr/bin/python3

import glob
import json
import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import ssl

config = {}
try:
   with open('config.json') as json_data:
        config = json.load(json_data)
except Exception as e:
        logger.error("Config load failed")
        exit(1)

auth = {
    'username': config['username'],
    'password': config['password'],
}
pub_topic = 'home/inputs/'

gpio = [
        [26,"bin_int_heating_on"],
        [24,"bin_loznice_right"],
        [25,"bin_loznice_left"]
] 


GPIO.setmode(GPIO.BCM)

def callback(channel):
    # value zero means active
    if GPIO.input(channel): 
        send_msg(pub_topic + ch[channel],0)
    else:  
        send_msg(pub_topic + ch[channel],1)

ch = dict()
for g2 in gpio:
    GPIO.setup(g2[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(g2[0], GPIO.BOTH, callback=callback, bouncetime = 200)  
    ch[g2[0]] = g2[1]

def send_msg(topic,val):
    try:
        #print ("Send value: ",val," Topic",topic)
        #publish.single(topic,val,
        #hostname=config['mqtt_host'], port=config['mqtt_port'],
        #auth=auth, tls={})
        client.publish(topic,val,0,0)
    except:
         time.sleep(120)
    return

def on_connect(client, userdata, rc, *extra_params):
    #print('Connected with result code ' + str(rc))
    for g2 in gpio:
        #print ("Subscribe",pub_topic + g2[1] + '/set')
        #client.publish(pub_topic + g2[1],0,0,0)
        send_msg(pub_topic + g2[1],0 if GPIO.input(int(g2[0])) else 1 )

client = mqtt.Client(client_id='RPI-MQTT-IN'
        '', clean_session=True, userdata=None)
client.tls_set(ca_certs=None, certfile=None,
                keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.tls_insecure_set(False)
client.username_pw_set(config['username'], password=config['password'])
client.on_connect = on_connect
client.connect(config['mqtt_host'], port=config['mqtt_port'], keepalive=120)

try:
    client.loop_forever()
except KeyboardInterrupt:
     GPIO.cleanup()
