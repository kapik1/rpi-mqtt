import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import ssl


config = {}
try:
       with open('config.json') as json_data:
                   config = json.load(json_data)
except Exception as e:
            print("Config load failed")
            exit(1)

gpio = [
        [14,"bin_out_heating"],
        [15,"bin_out_light_gate"],
        [18,"bin_out_light_door"],
        [23,"bin_out_light_court"]
]
pub_topic = 'home/outputs/'



def on_connect(client, userdata, rc, *extra_params):
    #print('Connected with result code ' + str(rc))
    for g2 in gpio:
        #print ("Subscribe",pub_topic + g2[1] + '/set')
        client.subscribe(pub_topic + g2[1] + '/set')
        client.publish(pub_topic + g2[1],0,0,0)


def on_message(client, userdata, msg):
    #print ('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    data = msg.topic.split("/")
    #print ("SET " + data[2] + " Gpio ", ch[data[2]] )
    client.publish(pub_topic + data[2],set_gpio_status(ch[data[2]],int(msg.payload)),0,0)


def set_gpio_status(pin, status):
    GPIO.output(pin, GPIO.LOW if status else GPIO.HIGH)
    return (1 if status else 0)


GPIO.setmode(GPIO.BCM)

ch = dict()
for g2 in gpio:
    #print ("Gpio setup",  g2[0])
    GPIO.setup(g2[0], GPIO.OUT, initial=GPIO.HIGH)
    ch[g2[1]] = g2[0]	



client = mqtt.Client(client_id='RPI-MQTT-OUT'
        '', clean_session=True, userdata=None)
client.tls_set(ca_certs=None, certfile=None,
                keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.tls_insecure_set(False)
client.username_pw_set(config['username'], password=config['password'])
client.on_connect = on_connect
client.on_message = on_message
client.connect(config['mqtt_host'], port=config['mqtt_port'], keepalive=120)


try:
    client.loop_forever()
except KeyboardInterrupt:
    GPIO.cleanup()
