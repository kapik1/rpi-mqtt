#!/usr/bin/python3

import glob
import json
import time
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO


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
        print ("Send value: ",val," Topic",topic,"\n")
        publish.single(topic,val,
        hostname=config['mqtt_host'], port=config['mqtt_port'],
        auth=auth, tls={})
    except:
         time.sleep(120)
    else:
         time.sleep(1)
    return

while True:
        time.sleep(100)       
