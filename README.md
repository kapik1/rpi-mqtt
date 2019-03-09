# rpi-mqtt
Reading multiple 1w DS1820 thermometers, slow digital inputs and digital outputs by raspberry pi and publish them to mqtt broker


# install
```
 git clone https://github.com/kapik1/rpi-mqtt.git
 cd rpi-mqtt
 
 apt-get install pip3
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
...
```



