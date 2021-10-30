#! /usr/bin/python

# Axpert Inverter control script

# Read values from inverter, sends values to mqtt,
# calculation of CRC is done by XMODEM

import time, sys, string
import sqlite3
import json
import datetime
import calendar
import os
import fcntl
import re
import crcmod
from binascii import unhexlify
import paho.mqtt.publish as mqtt
from random import randint





battery_types = {'0': 'AGM', '1': 'Flooded', '2': 'User'}
voltage_ranges = {'0': 'Appliance', '1': 'UPS'}
output_sources = {'0': 'utility', '1': 'solar', '2': 'battery'}
charger_sources = {'0': 'utility first', '1': 'solar first', '2': 'solar + utility', '3': 'solar only'}
machine_types = {'00': 'Grid tie', '01': 'Off Grid', '10': 'Hybrid'}
topologies = {'0': 'transformerless', '1': 'transformer'}
output_modes = {'0': 'single machine output', '1': 'parallel output', '2': 'Phase 1 of 3 Phase output', '3': 'Phase 2 of 3 Phase output', '4': 'Phase 3 of 3 Phase output'}
pv_ok_conditions = {'0': 'As long as one unit of inverters has connect PV, parallel system will consider PV OK', '1': 'Only All of inverters have connect PV, parallel system will consider PV OK'}
pv_power_balance = {'0': 'PV input max current will be the max charged current', '1': 'PV input max power will be the sum of the max charged power and loads power'}

debug = 0

# Config

config = {}
config['DEVICE'] = "/dev/hidraw0"
config['MQTT_SERVER'] = "*******.net"
config['MQTT_USER'] = "*****"
config['MQTT_PASS'] = "******"
config['MQTT_TOPIC'] = "power/axpert"
config['MQTT_TOPIC_ENERGY'] = "power/axpert/energy"
config['MQTT_TOPIC_SETTINGS'] = "power/axpert_settings"




# config 

def connect():
    global client
    if debug : print "test\n"
    if debug : print(config['DEVICE'])
    if debug : print(config['MQTT_SERVER'])

def serial_command(command):
    if debug : print(command)
    try:
        xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
        command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + '\x0d'

        try:
            if debug : print  "My debug:" + config['DEVICE'] + " Command:"  + command 
            file = open(config['DEVICE'], 'r+')
            fd = file.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        except Exception as e:
            print('error open file descriptor: ' + str(e))
            exit()
        
        os.write(fd, command_crc)

        time.sleep(0.3)
        response = ''
        timeout_counter = 0
        while '\r' not in response:
            if timeout_counter > 500:
                raise Exception('Read operation timed out')
            timeout_counter += 1
            try:
                response += os.read(fd, 100)
            except Exception as e:
                #print("error reading response...: " + str(e) + "  |" + response )
                time.sleep(0.01)
            if len(response) > 0 and response[0] != '(' or 'NAKss' in response:
                raise Exception('NAKss')

        if debug : print(response)
        response = response.rstrip()
        lastI = response.find('\r')
        response = response[1:lastI-2]
        
        file.close()
        return response
    except Exception as e:
        print('error reading inverter...: ' + str(e))
        file.close()
        time.sleep(10)
        connect()
        return serial_command(command)

def get_parallel_data():
    #collect data from axpert inverter
    try:
        data = '{'
        response = serial_command('QPGS0')
        nums = response.split(' ')
        if len(nums) < 27:
            return ''

        if nums[2] == 'L':
            data += '"Gridmode":1'
        else:
            data += '"Gridmode":0'
        data += ',"SerialNumber": ' + str(int(nums[1]))
        data += ',"BatteryChargingCurrent": ' + str(int(nums[12]))
        data += ',"BatteryDischargeCurrent": ' + str(int(nums[26]))
        data += ',"TotalChargingCurrent": ' + str(int(nums[15]))
        data += ',"GridVoltage": ' + str(float(nums[4]))
        data += ',"GridFrequency": ' + str(float(nums[5]))
        data += ',"OutputVoltage": ' + str(float(nums[6]))
        data += ',"OutputFrequency": ' + str(float(nums[7]))
        data += ',"OutputAparentPower": ' + str(int(nums[8]))
        data += ',"OutputActivePower": ' + str(int(nums[9]))
        data += ',"LoadPercentage": ' + str(int(nums[10]))
        data += ',"BatteryVoltage": ' + str(float(nums[11]))
        data += ',"BatteryCapacity": ' + str(float(nums[13]))
        data += ',"PvInputVoltage": ' + str(float(nums[14]))
        data += ',"TotalAcOutputApparentPower": ' + str(int(nums[16]))
        data += ',"TotalAcOutputActivePower": ' + str(int(nums[17]))
        data += ',"TotalAcOutputPercentage": ' + str(int(nums[18]))
        # data += ',"InverterStatus": ' + nums[19]
        data += ',"OutputMode": ' + str(int(nums[20]))
        data += ',"ChargerSourcePriority": ' + str(int(nums[21]))
        data += ',"MaxChargeCurrent": ' + str(int(nums[22]))
        data += ',"MaxChargerRange": ' + str(int(nums[23]))
        data += ',"MaxAcChargerCurrent": ' + str(int(nums[24]))
        data += ',"PvInputCurrentForBattery": ' + str(int(nums[25]))
        if nums[2] == 'B':
            data += ',"Solarmode":1'
        else:
            data += ',"Solarmode":0'

        data += '}'
    except Exception as e:
        print('error parsing inverter data...: ' + str(e))
        return ''
    return data

def get_data():
    #collect data from axpert inverter
    try:
        response = serial_command('QPIGS')
        #print "My response" + response + "/n"
        nums = response.split(' ')
        if len(nums) < 21:
            return ''

        data = '{'

        data += '"GridVoltage": ' + str(float(nums[0]))
        data += ',"GridFrequency": ' + str(float(nums[1]))
        data += ',"OutputVoltage": ' + str(float(nums[2]))
        data += ',"OutputFrequency": ' + str(float(nums[3]))
        data += ',"OutputAparentPower": ' + str(int(nums[4]))
        data += ',"OutputActivePower": ' + str(int(nums[5]))
        data += ',"LoadPercentage": ' + str(int(nums[6]))
        data += ',"BusVoltage":' + str(float(nums[7]))
        data += ',"BatteryVoltage": ' + str(float(nums[8]))
        data += ',"BatteryChargingCurrent": ' + str(int(nums[9]))
        data += ',"BatteryCapacity": ' + str(float(nums[10]))
        data += ',"InverterHeatsinkTemperature":' + str(float(nums[11]))

        data += ',"PvInputCurrent":' + str(float(nums[12]))
        data += ',"PvInputVoltage":' + str(float(nums[13]))
        data += ',"BatteryVoltageFromScc":' + str(float(nums[14]))
        data += ',"BatteryDischargeCurrent":' + str(int(nums[15]))
        # data += ',"DeviceStatus":"' + nums[16] + '"'

        data += ',"PvInputPower":' + str(int(nums[19]))

        data += '}'
        return data
    except Exception as e:
        print('error parsing inverter data...: ' + str(e))
        return ''

def get_settings():
    #collect data from axpert inverter
    try:
        response = serial_command('QPIRI')
        nums = response.split(' ')
        if len(nums) < 21:
            return ''

        data = '{'

        data += '"AcInputVoltage":' + str(float(nums[0]))
        data += ',"AcInputCurrent":' + str(float(nums[1]))
        data += ',"AcOutputVoltage":' + str(float(nums[2]))
        data += ',"AcOutputFrequency":' + str(float(nums[3]))
        data += ',"AcOutputCurrent":' + str(float(nums[4]))
        data += ',"AcOutputApparentPower":' + str(int(nums[5]))
        data += ',"AcOutputActivePower":' + str(int(nums[6]))
        data += ',"BatteryVoltage":' + str(float(nums[7]))
        data += ',"BatteryRechargeVoltage":' + str(float(nums[8]))
        data += ',"BatteryUnderVoltage":' + str(float(nums[9]))
        data += ',"BatteryBulkVoltage":' + str(float(nums[10]))
        data += ',"BatteryFloatVoltage":' + str(float(nums[11]))
        data += ',"BatteryType":"' + battery_types[nums[12]] + '"'
        data += ',"MaxAcChargingCurrent":' + str(int(nums[13]))
        data += ',"MaxChargingCurrent":' + str(int(nums[14]))
        data += ',"InputVoltageRange":"' + voltage_ranges[nums[15]] + '"'
        data += ',"OutputSourcePriority":"' + output_sources[nums[16]] + '"'
        data += ',"ChargerSourcePriority":"' + charger_sources[nums[17]] + '"'
        data += ',"MaxParallelUnits":' + str(int(nums[18]))
        data += ',"MachineType":"' + machine_types[nums[19]] + '"'
        data += ',"Topology":"' + topologies[nums[20]] + '"'
        data += ',"OutputMode":"' + output_modes[nums[21]] + '"'
        data += ',"BatteryRedischargeVoltage":' + str(float(nums[22]))
        data += ',"PvOkCondition":"' + pv_ok_conditions[nums[23]] + '"'
        data += ',"PvPowerBalance":"' + pv_power_balance[nums[24]] + '"'
#        data += ',"MaxBatteryCvChargingTime":' + str(int(nums[25]))
        
        data += '}'
        return data
    except Exception as e:
        print('error parsing inverter data...: ' + str(e))
        return ''

def get_QET():
    #collect data from axpert inverter
    try:
        data = '{'
        response = serial_command('QET')
        nums = response.split(' ')
        if len(nums) < 1:
            return ''

        data = '{'

        data += '"TotalEnergy":' + str(float(nums[0]))

        data += '}'
    except Exception as e:
        print('error parsing inverter data...: ' + str(e))
        return ''
    return data

def main():
    time.sleep(randint(0, 5)) # so parallel streams might start at different times
    connect();
    serial_number = serial_command('QID')
    if debug : print('Reading from inverter ' + serial_number)
    while True:
        #data = get_parallel_data()
        # data = '{"TotalAcOutputActivePower": 1000}'
        #if not data == '':
        #    send = send_data(data, config['MQTT_TOPIC_PARALLEL'])

        time.sleep(1)
        
        data = get_data()
        #if debug : print data
        if not data == '':
            try:
                auth = {
                       'username': config['MQTT_USER'],
                       'password': config['MQTT_PASS'],
                }
                if debug :  print   "_____"+config['MQTT_TOPIC']+"_____\n"
                mqtt.single(config['MQTT_TOPIC'], data,
                #mqtt.single("test", datan,
                        hostname=config['MQTT_SERVER'], port=8883,retain=1,qos=2,
                        auth=auth, tls={})
            except Exception as e:
                if debug : print "exception" + str(e)
                time.sleep(120)
            else:
                time.sleep(2)
        
        data = get_settings()
        if not data == '':
            try:
                auth = {
                       'username': config['MQTT_USER'],
                       'password': config['MQTT_PASS'],
                }
                if debug :  print   "_____"+config['MQTT_TOPIC_SETTINGS']+"_____\n"
                mqtt.single(config['MQTT_TOPIC_SETTINGS'], data,
                #mqtt.single("test", data,
                        hostname=config['MQTT_SERVER'], port=8883,retain=1,qos=2,
                        auth=auth, tls={})
            except Exception as e:
                if debug : print "exception" + str(e)
                time.sleep(120)
            else:
                time.sleep(2)

                

        data = get_QET()
        if not data == '':
            try:
                auth = {
                       'username': config['MQTT_USER'],
                       'password': config['MQTT_PASS'],
                }
                if debug :  print   "_____"+config['MQTT_TOPIC_ENERGY']+"_____\n"
                mqtt.single(config['MQTT_TOPIC_ENERGY'], data,
                #mqtt.single("test", datan,
                        hostname=config['MQTT_SERVER'], port=8883,retain=1,qos=2,
                        auth=auth, tls={})
            except Exception as e:
                if debug : print "exception" + str(e)
                time.sleep(120)
            else:
                time.sleep(2)
        time.sleep(60)

if __name__ == '__main__':
    main()
