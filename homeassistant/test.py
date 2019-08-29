#!/usr/bin/python3

import logging
import logging.handlers
import time

from Unipi import Blinds

def on_state(position):
    print("www3")
    print("Position %s" % (position))
    print("www4")

b = Blinds(ws, 'led', '1_02', '1_03', state_callback = on_state)

b.go_to(100)
time.sleep(100)
