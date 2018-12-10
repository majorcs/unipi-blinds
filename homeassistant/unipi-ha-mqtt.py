#!/usr/bin/python3

import json
import logging
import logging.handlers
import paho.mqtt.client as mqtt
import sys
import time
import traceback
import websocket

from threading import Timer,Thread,Event
from Unipi import Blinds


logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)
mylog = logging.getLogger('MyLogger')
# handler = logging.handlers.SysLogHandler(address = '/dev/log')
#mylog.addHandler(handler)


def on_log(client, userdata, level, buf):
    mylog.debug("[MQTT]ONLOG: %s, %s, %s, %s" % (client, userdata, level, buf))

def on_ws_message(ws, message):
    obj = json.loads(message)
    mylog.debug(message)
    for single_obj in obj:
        dev = single_obj['dev']
        circuit = single_obj['circuit']
        value = single_obj['value']
        mylog.info("[WEBSOCKET]Value: " + str(value) + " Device: " + str(dev) + " Circuit: " + str(circuit))
  
def on_ws_error(ws, error):
    mylog.error("[WEBSOCKET]%s" % (error))

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

    client.subscribe("homeassistant/cover/#")

def on_mqtt_disconnect(client, userdata, rc):
    mylog.info("[MQTT]Disconnected")

if __name__ == "__main__":
    devices = []
    url = "ws://192.168.88.32:8080/ws"
    ws = websocket.WebSocket()

    client = mqtt.Client()
    client.on_connect = on_mqtt_connect
    client.on_disconnect = on_mqtt_disconnect
    #client.on_log = on_log
    client.enable_logger(mylog)
    client.connect("192.168.88.24", 1883, 60)

    #receiving messages
    ws = websocket.WebSocketApp(url, on_open = on_ws_open, on_message = on_ws_message, on_error = on_ws_error, on_close = on_ws_close)
    b = [
            Blinds('redony_uj_01', ws, client, 'led', '1_01', '1_02'),
            Blinds('redony_uj_02', ws, client, 'led', '1_03', '1_04')
        ]

    client.loop_start()
    ws.run_forever()
    mylog.debug("WS stopped")

    client.disconnect()
    client.loop_stop(force=False)
