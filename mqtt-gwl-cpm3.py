#!/usr/bin/python3

import glob
import json
import time
import eventlet
import requests
import xmltodict
import paho.mqtt.publish as publish
eventlet.monkey_patch()


config = {}
try:
   with open('/home/pi/rpi-mqtt/config.json') as json_data:
        config = json.load(json_data)
except Exception as e:
        logger.error("Config load failed")
        exit(1)

auth = {
    'username': config['username'],
    'password': config['password'],
}
pub_topic = '/home/gwl/bms/'
url =  'http://' + config['cpm_url'] +'/bcc.xml'

while True:
    try:
       with eventlet.Timeout(10):
          response = requests.get(url, verify=False)
    except:
        # print("Exception \n")
        time.sleep(60)
        # print("Exception next \n")
    else:    
       dict_data = xmltodict.parse(response.content)
       d = dict_data['data']

       for key in d:    
           # print(key + " " +dict_data['data'][key]  )
           if dict_data['data'][key]  is not 'N/A':
               try:
                  publish.single(pub_topic + key, str( dict_data['data'][key]),
                        hostname=config['mqtt_host'], port=config['mqtt_port'],retain=1,qos=2,
                        auth=auth, tls={})
               except:
                  time.sleep(120)
               else:
                  time.sleep(0.1)
           time.sleep(0.1)
    time.sleep(120)
