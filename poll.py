#!/usr/bin/python

import select

poll_object = select.poll()
#fd_object = file("/sys/class/hwmon/hwmon1/temp2_input", "r")
fd_object = file("/sys/class/hwmon/hwmon0/temp1_input", "r")
poll_object.register(fd_object) # I use the select.POLLPRI | select.POLLERR combination in my code ;)
result = poll_object.poll()

print(result)
