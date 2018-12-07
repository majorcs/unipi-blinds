HomeAssistant integration for UniPi Neuron
==========================================

This small script tries to do a seamless integration between UniPi Neuron and HomeAssistant (HA).
HA supports so-called MQTT discovery. You can create Unipi related object and those should be automatically
detected by your HA. Currently only timed-blinds device is supported which can open, close or position the 
blinds to a position. This needs two relays output on the UniPi defined in the Blinds object.

The UniPi is controlled over WebSocket API, the HA intehration uses MQTT interface.


More to come...


