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
        ["10-000000402bfe","temp_int_boiler_inlet"],
        ["10-000000403a79","temp_int_boiler_bottom"],
        ["28-00000271a53b","temp_int_outdoor_north"],
        ["28-00000272109a","temp_int_outdoor_south"],
        ["28-000002722a65","temp_int_boiler_top"],
        ["28-0000027245f4","temp_int_boiler_middle"],
        ["28-000002726502","temp_int_solar_pannel"],
        ["28-000002728c5c","temp_int_boiler_outlet"],
        ["28-00000272b64e","temp_int_boiler_room"],
        ["28-0000027231b7","temp_int_heating_backward"],
        ["28-00000272c3c9","temp_int_hall_room"],
        ["28-00000272f500","temp_int_heating_input"]
]


base_dir = '/sys/bus/w1/devices/'
device_file = '/w1_slave'

def read_temp(t_id):
    valid = False
    temp = 0
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


while True:
    for tl in termo:    
        temp = read_temp(tl[0])
        # print ("Read ",tl[0],"Value: ",temp," Topic",pub_topic + tl[1],"\n")
        if temp is not None:
            try:
                publish.single(pub_topic + tl[1], str(temp),
                        hostname=config['mqtt_host'], port=config['mqtt_port'],
                        auth=auth, tls={})
            except:
                time.sleep(120)
            else:
                time.sleep(2)
        time.sleep(2)
    time.sleep(120)
