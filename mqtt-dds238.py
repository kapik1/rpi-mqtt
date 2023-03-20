#!/usr/bin/python3

import glob
import json
import time
import paho.mqtt.publish as publish
from dds238 import DDS238



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

pub_topic = 'home/dds238/'
dds238 = [
        [137,"m1_out"],
        [26,"m1_in"],
]


device_file = '/dev/ttyUSB0'

def read_dds238(met_id,sub_topic):
     #print ("meter ID ",  met_id ,"Subtopic: ", sub_topic ,"\n")
     meter = DDS238(modbus_device=device_file, meter_id=met_id)
     try:
          mqtt_publish (meter.voltage, sub_topic + 'voltage' )
          mqtt_publish (meter.current , sub_topic + 'current' )
          mqtt_publish (meter.frequency , sub_topic + 'frequency' )
          mqtt_publish (meter.power , sub_topic + 'power' )
          mqtt_publish (meter.reactive_power , sub_topic + 'reactive_power' )
          mqtt_publish (meter.power_factor , sub_topic + 'power_factor' )
          mqtt_publish (meter.import_energy , sub_topic + 'import_energy' )
          mqtt_publish (meter.export_energy , sub_topic + 'export_energy' )
     except:
          1

def mqtt_publish(value,topic):
    try:
        publish.single(pub_topic + '/' +  topic, value,
            hostname=config['mqtt_host'], port=config['mqtt_port'],retain=1,qos=2,
            auth=auth, tls={})
    except:
        time.sleep(120)
    else:
        1

while True:
    for dds in dds238:
        meter_id = dds[0]
        sub_topic = dds[1]
        #print ("meter ID ",  meter_id ,"Subtopic: ", sub_topic ,"\n")
        read_dds238(meter_id,pub_topic + sub_topic + '/')
    time.sleep(60)
