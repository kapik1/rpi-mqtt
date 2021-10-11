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
        [26,"bin_int_heating_on",0,10],
        [24,"bin_loznice_left","ON","OFF"],
        [25,"bin_loznice_right","ON","OFF"]
] 


GPIO.setmode(GPIO.BCM)

def callback(channel):
    # value zero means active
    time.sleep(0.2)
    inp=GPIO.input(channel)
    #print ("Callback ch:"+str(channel)+"value"+ str(inp))
    
    if inp  != ch_state[channel]:
      if inp: 
           send_msg(pub_topic + ch[channel],ch_off[channel])
           ch_state[channel] = 1
           #print ("Callback OFF")
      else:  
           send_msg(pub_topic + ch[channel],ch_on[channel])
           ch_state[channel] = 0
           #print ("Callback ON")

ch = dict()
ch_on = dict()
ch_off = dict()
ch_state = dict()

for g2 in gpio:
    GPIO.setup(g2[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.add_event_detect(g2[0], GPIO.BOTH, callback=callback, bouncetime = 350)  
    GPIO.add_event_detect(g2[0], GPIO.BOTH, callback=callback)  
    ch[g2[0]] = g2[1]
    ch_on[g2[0]] = g2[2]
    ch_off[g2[0]] = g2[3]

def send_msg(topic,val):
    try:
        #print ("Send value: ",val," Topic",topic)
        #publish.single(topic,val,
        #hostname=config['mqtt_host'], port=config['mqtt_port'],
        #auth=auth, tls={})
        client.publish(topic,val,2,1)
    except:
         time.sleep(1)
    return

def on_connect(client, userdata, rc, *extra_params):
    #print('Connected with result code ' + str(rc))
    for g2 in gpio:
        #print ("Subscribe",pub_topic + g2[1] + '/set')
        #client.publish(pub_topic + g2[1],0,0,0)
        ch_state[int(g2[0])] =  GPIO.input(int(g2[0]))
        send_msg(pub_topic + g2[1],ch_off[int(g2[0])] if GPIO.input(int(g2[0])) else ch_on[int(g2[0])] )

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
