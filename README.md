# rpi-mqtt
Reading multiple 1w DS1820 thermometers, slow digital inputs and digital outputs by raspberry pi and publish them to mqtt broker


# run it on startup

cat /etc/rc.local

...
\# Read 1w temperatures
cd /root/rpi-mqtt
/root/rpi-mqtt/mqtt-temp &
....




