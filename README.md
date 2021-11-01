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
 pip3 install RPi.GPIO
 
 ./mqtt-temp
 
```


# run it on startup





```
root@raspberrypi:/etc/supervisor/conf.d# cat mqtt-bin-in.conf
[program:mqtt-bin-in]
process_name=%(program_name)s_%(process_num)02d
directory=/home/pi/rpi-mqtt/
command=/home/pi/rpi-mqtt/mqtt-bin-in.py
autostart=true
autorestart=true
user=pi
numprocs=1
redirect_stderr=true
stdout_logfile=/home/pi/rpi-mqtt/mqtt-bin-in.log


root@raspberrypi:/etc/supervisor/conf.d# cat mqtt-bin-out.conf
[program:mqtt-bin-out]
process_name=%(program_name)s_%(process_num)02d
directory=/home/pi/rpi-mqtt/
command=python3 /home/pi/rpi-mqtt/mqtt-bin-out.py
autostart=true
autorestart=true
user=pi
numprocs=1
redirect_stderr=true
stdout_logfile=/home/pi/rpi-mqtt/mqtt-bin-out.log

root@raspberrypi:/etc/supervisor/conf.d# cat mqtt-temp.conf
[program:mqtt-temp]
process_name=%(program_name)s_%(process_num)02d
directory=/home/pi/rpi-mqtt/
command=/home/pi/rpi-mqtt/mqtt-temp.py
autostart=true
autorestart=true
user=pi
numprocs=1
redirect_stderr=true
stdout_logfile=/home/pi/rpi-mqtt/mqtt-temp.log

root@raspberrypi:/etc/supervisor/conf.d# cat mqtt-gwl-cpm.conf
[program:mqtt-gwl-cpm3]
process_name=%(program_name)s_%(process_num)02d
directory=/home/pi/rpi-mqtt/
command=/home/pi/rpi-mqtt/mqtt-gwl-cpm3.py
autostart=true
autorestart=true
user=pi
numprocs=1
redirect_stderr=true
stdout_logfile=/home/pi/rpi-mqtt/mqtt-gwl-cpm3.log


To enable read serial raw interface 
# cat /etc/udev/rules.d/999-hid.rules
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", MODE="0664", GROUP="plugdev"


# cat /etc/supervisor/conf.d/mqtt-aexpert.conf
[program:mqtt-axpert]
process_name=%(program_name)s_%(process_num)02d
directory=/home/pi/rpi-mqtt/
command=/home/pi/rpi-mqtt/mqtt-axpert.py
autostart=true
autorestart=true
user=pi
numprocs=1
redirect_stderr=true
stdout_logfile=/home/pi/rpi-mqtt/mqtt-axpert.log




supervisorctl  update

root@raspberrypi:~# supervisorctl status
mqtt-bin-in:mqtt-bin-in_00       RUNNING   pid 1115, uptime 0:09:13
mqtt-bin-out:mqtt-bin-out_00     RUNNING   pid 1321, uptime 0:00:08
mqtt-temp:mqtt-temp_00           RUNNING   pid 992, uptime 0:23:22



```



