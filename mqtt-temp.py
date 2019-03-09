#!/usr/bin/python3

import glob
import json
import time
import paho.mqtt.publish as publish

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

pub_topic = 'home/temperature/'
termo = [
        ["28-00000a4ac5ae","temp_int_portable"],
]


base_dir = '/sys/bus/w1/devices/'
device_file = '/w1_slave'

def read_temp(t_id):
    valid = False
    temp = 0
    try:
      with open(base_dir + t_id + device_file , 'r') as f:
        for line in f:
            if line.strip()[-3:] == 'YES':
                valid = True
            temp_pos = line.find(' t=')
            if temp_pos != -1:
                temp = round(float(line[temp_pos + 3:]) / 1000.0,1)

      if valid:
        return temp
      else:
        return None
    except:
        # device missing on the bus
        return None
    else:
        return


while True:
    for tl in termo:    
        temp = read_temp(tl[0])
        print ("Read ",tl[0],"Value: ",temp," Topic",pub_topic + tl[1],"\n")
        if temp is not None:
            try:
                publish.single(pub_topic + tl[1], str(temp),
                        hostname=config['mqtt_host'], port=config['mqtt_port'],
                        auth=auth, tls={})
            except:
                # Broker is unreachable
                time.sleep(120)
            else:
                time.sleep(2)
        time.sleep(2)
    time.sleep(120)
