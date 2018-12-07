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
        self.position = 100
        self.orig_position = self.position
        self.new_position = self.position
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
            logging.debug("New position: %s" % self.position)
            if (self.position > 100) or (self.position < 0):
                self.position = min(max(0, self.position), 100)
                logging.error("Position overrun; stop and set back to: %s" % self.position)
                self.stop()
            else:
                Timer(0.5, self.send_state_update).start()

        self.mqtt.publish('homeassistant/cover/position', payload=self.position)

    def go(self, sleep_time, device, circuit):
        logging.debug("GO: %s, %s, %s" % (device, circuit, self.state))
        self.ws_call(device, circuit, 1)
        self.start_time = time.time()
        self.timer = Timer(sleep_time, self.stop, None, {'timer': True})
        self.timer.start()
        self.send_state_update()

    def stop(self, timer=False):
        if timer:
            self.position = self.new_position
            self.send_state_update()
        elif hasattr(self, 'timer'):
            self.timer.cancel()
            self.timer = None
        logging.debug("STOP; POS: %s" % (self.position))
        self.ws_call(self.device, self.up_circuit, 0)
        self.ws_call(self.device, self.down_circuit, 0)
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
        position = min(max(0, position), 100)
        
        logging.info("Going to: %s" % (position))
        self.orig_position = self.position
        diff = self.position - position
        t = (abs(diff)/100)*self.timers['full']
        if (t > 1):
            if diff < 0:
                self.go_down(t)
            else:
                self.go_up(t)
        self.new_position = position
