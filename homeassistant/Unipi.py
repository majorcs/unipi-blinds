#!/usr/bin/python3

from pprint import pprint
from threading import Timer,Thread,Event

import json
import logging
import re
import requests
import time
import websocket

# curl --request POST --url 'http://192.168.88.32:8080/rest/relay/3_01' --data 'mode=simple&value=1'

class Blinds:
    def __init__(self, ws, device, up_circuit, down_circuit, timer_full = 20, timer_partial = 10):
        self.position = 0
        self.timers = {}
        self.timers['full'] = timer_full
        self.timers['partial'] = timer_partial
        self.device = device
        self.up_circuit = up_circuit
        self.down_circuit = down_circuit
        self.ws = ws

    def ws_call(self, device, circuit, value):
        wsmsg = json.dumps({"cmd": "set", "dev": device, "circuit": circuit, "value": value})
        logging.debug("ws_call: "+wsmsg)
        self.ws.send(wsmsg)

    def go(self, sleep_time, device, circuit):
        logging.debug("GO: %s, %s" % (device, circuit))
        self.ws_call(device, circuit, 1)
        Timer(sleep_time, lambda: self.stop(device, circuit)).start()

    def stop(self, device, circuit):
        logging.debug("STOP: %s, %s" % (device, circuit))
        self.ws_call(device, circuit, 0)

    def go_up(self, sleep_time):
        logging.info("Going up for %s seconds" % (sleep_time))
        self.go(sleep_time, self.device, self.up_circuit)

    def go_down(self, sleep_time):
        logging.info("Going down for %s seconds" % (sleep_time))
        self.go(sleep_time, self.device, self.down_circuit)
        
    def go_to(self, position):
        logging.info("Going to: %s" % (position))
        diff = self.position - position
        t = (abs(diff)/100)*self.timers['full']
        if diff < 0:
            self.go_down(t)
        else:
            self.go_up(t)
        self.position = position
