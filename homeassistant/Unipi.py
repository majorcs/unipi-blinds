#!/usr/bin/python3

from pprint import pprint
from threading import Timer,Thread,Event

import json
import logging
import re
import requests
import time
import websocket

class Blinds:
    def __init__(self, ws, mqtt, device, up_circuit, down_circuit, timer_full = 20, timer_partial = 10):
        self.position = 0
        self.timers = {}
        self.timers['full'] = timer_full
        self.timers['partial'] = timer_partial
        self.device = device
        self.up_circuit = up_circuit
        self.down_circuit = down_circuit
        self.ws = ws
        self.mqtt = mqtt
        self.state = 0

    def ws_call(self, device, circuit, value):
        wsmsg = json.dumps({"cmd": "set", "dev": device, "circuit": circuit, "value": value})
        logging.debug("ws_call: "+wsmsg)
        self.ws.send(wsmsg)

    def send_state_update(self):
        if self.state != 0:
            diff = int((time.time() - self.start_time) / self.timers['full'] * 100)
            if self.state == 1:
                self.position = self.orig_position - diff
            if self.state == 2:
                self.position = self.orig_position + diff
            print(self.position)
            self.mqtt.publish('DEMO', payload=self.position)

            Timer(0.5, self.send_state_update).start()

    def go(self, sleep_time, device, circuit):
        logging.debug("GO: %s, %s, %s" % (device, circuit, self.state))
        self.ws_call(device, circuit, 1)
        self.start_time = time.time()
        Timer(sleep_time, lambda: self.stop(device, circuit, timer=True)).start()
        self.send_state_update()

    def stop(self, device, circuit, timer=False):
        if timer:
            self.position = self.new_position
        logging.debug("STOP: %s, %s; POS: %s" % (device, circuit, self.position))
        self.ws_call(device, circuit, 0)
        self.state = 0

    def go_up(self, sleep_time):
        logging.info("Going up for %s seconds" % (sleep_time))
        self.state = 1
        self.go(sleep_time, self.device, self.up_circuit)

    def go_down(self, sleep_time):
        logging.info("Going down for %s seconds" % (sleep_time))
        self.state = 2
        self.go(sleep_time, self.device, self.down_circuit)
        
    def go_to(self, position):
        if position > 100:
            position = 100
        if position < 0:
            position = 0
        logging.info("Going to: %s" % (position))
        self.orig_position = self.position
        diff = self.position - position
        t = (abs(diff)/100)*self.timers['full']
        if diff < 0:
            self.go_down(t)
        else:
            self.go_up(t)
        self.new_position = position
