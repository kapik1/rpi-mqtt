# rpi-mqtt
Reading multiple 1w DS1820 thermometers, digital inputs and digital outputs by raspberry pi and publish them to mqtt broker


# Config - temperatures

```
pub_topic = 'home/temperature/'
termo = [
        ["28-00000271a53b","temp_outdoor_north"],
        ["28-00000272109a","temp_outdoor_south"]
]
```
topic: home/temperature/temp_outdoor_north value: temperature in celsius 

# Config - inputs

gpio number and topic

```
pub_topic = 'home/inputs/'
gpio = [
        [26,"bin_heating_runing"],
        [24,"bin_switch_right"],
        [25,"bin_switch_left"]
]
```

topic: home/inputs/bin_switch_right value: 1 or 0

# Config - inputs

gpio number and topic

```
pub_topic = 'home/outputs/'
gpio = [
        [14,"bin_out_heating_request"]
]
```

topic: home/outputs/bin_out_heating_request value: 1 or 0

Controll

topic: home/outputs/bin_out_heating_request/set value: 1 or 0





# install
```
 apt-get install git
 git clone https://github.com/kapik1/rpi-mqtt.git
 cd rpi-mqtt
 
 apt-get install python3-pip
 pip3 install setuptools
 pip3 install paho-mqtt
 
 ./mqtt-temp
 
```


# run it on startup





```
cat /etc/rc.local

...
# Read 1w temperatures
cd /root/rpi-mqtt
/root/rpi-mqtt/mqtt-temp.py &
/root/rpi-mqtt/mqtt-bin-in.py &
/root/rpi-mqtt/mqtt-bin-out.py &
...
```



