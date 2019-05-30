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
    def __init__(self, id, ws, mqtt, device, up_circuit, down_circuit, timer_full = 20, timer_partial = 10):
        self.position = 100
        self.id = id
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
        self.state = -1
        self.autoconfig()

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            logging.debug("[BLINDSMQTT/%s]%s: %s" % (self, msg.topic, payload))
            if (msg.topic == "homeassistant/cover/%s/set_position" % self.id):
                self.go_to(int(payload))
            if (msg.topic == "homeassistant/cover/%s/set" % self.id):
                logging.debug("SETTING blinds to a state")
                if (payload == "OPEN"):
                    self.go_to(100)
                if (payload == "CLOSE"):
                    self.go_to(0)
                if (payload == "STOP"):
                    self.stop()
        except Exception as e:
            print("ERROR: %s" % e)
            traceback.print_exc()

    def autoconfig(self):
        self.mqtt.publish('homeassistant/cover/%s/config' % (self.id), '', retain=True)
        self.mqtt.publish('homeassistant/cover/%s/config' % (self.id),
            json.dumps({"unique_id": self.id, "name": self.id,
                        "command_topic": "homeassistant/cover/%s/set" % self.id,
                        "position_topic": "homeassistant/cover/%s/position" % self.id,
                        "set_position_topic": "homeassistant/cover/%s/set_position" % self.id,
                        "qos": 0,
                        "retain": True,
                        "payload_open": "OPEN",
                        "payload_close": "CLOSE",
                        "payload_stop": "STOP",
                        "position_open": 100,
                        "position_closed": 0,
                        "optimistic": False
            }), retain=True)
        self.mqtt.message_callback_add("homeassistant/cover/%s/set_position" % self.id, self.on_mqtt_message)
        self.mqtt.message_callback_add("homeassistant/cover/%s/set" % self.id, self.on_mqtt_message)


    def ws_call(self, device, circuit, value):
        wsmsg = json.dumps({"cmd": "set", "dev": device, "circuit": circuit, "value": value})
        logging.debug("ws_call: "+wsmsg)
        self.ws.send(wsmsg)

    def send_state_update(self):
        if self.state > 0:
            diff = int((time.time() - self.start_time) / self.timers['full'] * 100)
            if self.state == 1:
                self.position = self.orig_position - diff
            if self.state == 2:
                self.position = self.orig_position + diff
            logging.debug("New position: %s; destination: %s" % (self.position, self.new_position))
            if (self.position > 100) or (self.position < 0):
                self.position = min(max(0, self.position), 100)
                logging.error("Position overrun; stop and set back to: %s" % self.position)
                self.stop()
            else:
                Timer(1, self.send_state_update).start()

        self.mqtt.publish('homeassistant/cover/%s/position' % self.id, payload=self.position)

    def go(self, sleep_time, device, circuit):
        logging.debug("GO: %s, %s, %s" % (device, circuit, self.state))
        self.ws_call(device, circuit, 1)
        self.start_time = time.time()
        self.timer = Timer(sleep_time, self.stop, None, {'timer': True})
        self.timer.start()
        self.send_state_update()

    def clear_timer(self):
        self.state = 0
        if hasattr(self, 'timer') and self.timer:
            self.timer.cancel()
            self.timer = None

    def stop(self, timer=False):
        self.state = 0
        if timer:
            self.position = self.new_position
            self.send_state_update()
        self.clear_timer()
        logging.debug("STOP; POS: %s" % (self.position))
        self.ws_call(self.device, self.up_circuit, 0)
        self.ws_call(self.device, self.down_circuit, 0)

    def go_up(self, sleep_time):
        logging.info("Going up for %s seconds" % (sleep_time))
        self.state = 1
        self.go(sleep_time, self.device, self.up_circuit)

    def go_down(self, sleep_time):
        logging.info("Going down for %s seconds" % (sleep_time))
        self.state = 2
        self.go(sleep_time, self.device, self.down_circuit)
        
    def go_to(self, position):
        logging.debug("STATE: %s" %(self.state))
        if self.state > 0:
            return

        # state is unknown yet
        if self.state == -1:
            # assume we're on the opposite position
            if position > 50:
                self.position = 0
            else:
                self.position = 100
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
