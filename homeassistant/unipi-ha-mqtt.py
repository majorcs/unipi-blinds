#!/usr/bin/python3

import json
import logging
import logging.handlers
import paho.mqtt.client as mqtt
import time
import websocket

from threading import Timer,Thread,Event
from Unipi import Blinds

tmsg=''

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        global tmsg
        while not self.stopped.wait(0.5):
            print("my thread: "+tmsg)
            # call a function

devices = []
ws = websocket.WebSocket()

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)
mylog = logging.getLogger('MyLogger')
# handler = logging.handlers.SysLogHandler(address = '/dev/log')
#mylog.addHandler(handler)

url = "ws://192.168.88.32:8080/ws"

#stopFlag = Event()
#thread = MyThread(stopFlag)
#thread.start()

def on_ws_message(ws, message):
    obj = json.loads(message)
    mylog.debug(message)
    for single_obj in obj:
        dev = single_obj['dev']
        circuit = single_obj['circuit']
        value = single_obj['value']
        mylog.info("[WEBSOCKET]Value: " + str(value) + " Device: " + str(dev) + " Circuit: " + str(circuit))
  
def on_ws_error(ws, error):
    mylog.error("[WEBSOCKET]"+error)

def on_ws_close(ws):
    mylog.info("[WEBSOCKET]Connection closed")
  
def on_ws_open(ws):
    # Turn on filtering
    ws.send(json.dumps({"cmd":"filter", "devices":["temp", "input", "relay", "ao"]}))
    # Turn on DO 1.01
    # ws.send(json.dumps({"cmd":"set", "dev":"relay", "circuit": "1_01", "value":1}))
    # Query for complete status
    ws.send(json.dumps({"cmd":"all"}))

def on_mqtt_connect(client, userdata, flags, rc):
    mylog.info("[MQTT]Connected with result code "+str(rc))

    client.subscribe("#")

# The callback for when a PUBLISH message is received from the server.
def on_mqtt_message(client, userdata, msg):
    global tmsg
    tmsg = msg.topic+" "+str(msg.payload)
    mylog.info("[MQTT]"+msg.topic+" "+str(msg.payload))
    if (msg.topic == "mcs"):
        #ws.send(json.dumps({"cmd":"all"}))
        b.go_to(int(msg.payload))

client = mqtt.Client()
client.on_connect = on_mqtt_connect
client.on_message = on_mqtt_message
client.connect("192.168.88.24", 1883, 60)

#receiving messages
ws = websocket.WebSocketApp(url, on_open = on_ws_open, on_message = on_ws_message, on_error = on_ws_error, on_close = on_ws_close)
b = Blinds(ws, 'led', '1_02', '1_03')


client.loop_start()
ws.run_forever()
client.loop_stop(force=False)
#stopFlag.set()
