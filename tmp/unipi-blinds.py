#!/usr/bin/python3

from pprint import pprint
from urllib.parse import urljoin

import re
import requests
import time

# curl --request POST --url 'http://192.168.88.32:8080/rest/relay/3_01' --data 'mode=simple&value=1'

class Blinds:
    def __init__(self, api_url, up_device, down_device, timer_full = 20, timer_partial = 10):
        self.api_url = api_url
        self.position = 0
        self.timers = {}
        self.timers['full'] = timer_full
        self.timers['partial'] = timer_partial
        self.up_device = up_device
        self.down_device = down_device

    def rest_call(self, device, data):
        url = urljoin(self.api_url, device)
        print(url)
        print(data)
        r = requests.post(url, data)
        print(r.text)

    def go(self, sleep_time, device):
        self.rest_call(device, { 'value': 1 })
        time.sleep(sleep_time)
        self.rest_call(device, { 'value': 0 })

    def go_up(self, sleep_time):
        print("Going up for {} seconds".format(sleep_time))
        self.go(sleep_time, self.up_device)

    def go_down(self, sleep_time):
        print("Going down for {} seconds".format(sleep_time))
        self.go(sleep_time, self.down_device)
        
    def go_to(self, position):
        print("Going to: {}".format(position))
        diff = self.position - position
        t = (abs(diff)/100)*self.timers['full']
        if diff < 0:
            self.go_down(t)
        else:
            self.go_up(t)
        self.position = position
                    
        
#b = Blinds('http://192.168.88.32:8080/rest/', 'led/1_02', 'led/1_03' )
b = Blinds('http://192.168.88.32:8080/rest/', 'relay/3_13', 'relay/3_14' )
b.go_to(10)
time.sleep(2)
b.go_to(50)
time.sleep(2)
b.go_to(0)

pprint(vars(b))
