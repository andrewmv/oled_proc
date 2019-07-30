#!/usr/bin/python

# Andrew Villeneuve 2019
# Display system stats on I2C OLED screen

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import socket
import time
import os

## Init Device ##

# Select i2c/spi and address
serial = i2c(port=1, address=0x3C)

# Select driver chip (SSD130X)
device = ssd1306(serial)

## Draw Stuff ##

def gethostname():
    return socket.gethostname()

def getip():
    return socket.gethostbyname(gethostname())

def getloadavg():
    load = os.getloadavg()
    return '{one:.2}, {five:.2}, {fifteen:.2}'.format(one=load[0], five=load[1], fifteen=load[2])
    #return '{load.0:.2}, {load.1:.2}, {load.2:.2}'.format(load=load)

#def cpugraph(draw, x, y, width, height):

# Note: canvas is written to device when WITH block exits
frame = 0
while True:
    hostname = gethostname()
    ip = getip()
    with canvas(device) as draw:
    # Bounding Box
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        x = 3
        y = 3

    # Line 1: Host / IP 
        str = hostname + ' / ' + ip
        if (draw.textsize(str)[0] > device.width):
            if (frame % 2):
                str = ip
            else:
                str = host
        draw.text((x, y), str, fill="white")
        y += draw.textsize(str)[1] + 1

    # Line 2: loadavg - minigraph
        str = getloadavg()
        draw.text((x, y), str, fill="white")
        y += draw.textsize(str)[1] + 1

    # Line 3: Rx/Tx - minigraph

    time.sleep(1)
    frame+=1

