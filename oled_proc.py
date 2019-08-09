#!/usr/bin/python

# Andrew Villeneuve 2019
# Display system stats on I2C OLED screen

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import socket
import time
import os
import psutil
import ctypes
import netifaces as ni

## Init Device ##

# Select i2c/spi and address
serial = i2c(port=52, address=0x3C)

# Select driver chip (SSD130X)
device = ssd1306(serial, rotate=2)

hist_size = 32                 # Horizontal width (in px) of minigraphs
iface = 'enp1s0'               # Network interface to monitor
refresh = 1                    # Seconds per refresh

## Init Data ##
frame = 0       # Refresh counter
cpu_hist = [0] * hist_size
rx_hist =  [0] * hist_size
tx_hist =  [0] * hist_size
cpu_hist_i = 0
rx_hist_i = 0
tx_hist_i = 0
rx_sample = 0
tx_sample = 0

#Call and discard first value per docs
psutil.cpu_percent()

## Function Defs ##

def gethostname():
    return socket.gethostname()

def getip():
    if iface is None:
        return socket.gethostbyname(gethostname())
    else:
        return ni.ifaddresses(iface)[ni.AF_INET][0]['addr']

def getloadavg():
    load = os.getloadavg()
    return '{one:.2}, {five:.2}, {fifteen:.2}'.format(one=load[0], five=load[1], fifteen=load[2])

def cpugraph(draw, x, y, height):
    global cpu_hist_i
    cpu = psutil.cpu_percent()
    bar_height = (int)((cpu / 100) * height)
    cpu_hist[cpu_hist_i] = bar_height 
    for i in range(cpu_hist_i + 1, hist_size):
        draw.line([ x + i - cpu_hist_i, \
                    y + height, \
                    x + i - cpu_hist_i, \
                    y + height - cpu_hist[i]], \
                   fill="white", \
                   width=1)
    for i in range(0, cpu_hist_i):
        draw.line([ x + hist_size - cpu_hist_i + i, \
                    y + height, \
                    x + hist_size - cpu_hist_i + i, \
                    y + height - cpu_hist[i]], \
                   fill="white", \
                   width=1)
    cpu_hist_i += 1
    if cpu_hist_i >= hist_size:
        cpu_hist_i = 0

def getrxspeed():
    global rx_sample
    new_sample = psutil.net_io_counters().bytes_recv
    bps = new_sample - rx_sample
    rx_sample = new_sample
    return bps

def gettxspeed():
    global tx_sample
    new_sample = psutil.net_io_counters().bytes_sent
    bps = new_sample - tx_sample
    tx_sample = new_sample
    return bps

def pretty_speed(bps):
    if bps < (1 << 20): #kbps
        return '{speed:.2f} kB/s'.format(speed=float(bps)/(1 << 10))
    if bps < (1 << 30): #mbps
        return '{speed:.2f} MB/s'.format(speed=float(bps)/(1 << 20))
    if bps < (1 << 40): #gbps
        return '{speed:.2f} GB/s'.format(speed=float(bps)/(1 << 30))
    return "Error"

## Draw Stuff ##

# Note: canvas is written to device when WITH block exits
while True:
    hostname = gethostname()
    ip = getip()
    with canvas(device) as draw:
    # Bounding Box
        #draw.rectangle(device.bounding_box, outline="white", fill="black")
        x = 0
        y = 0

        # Line 1: Host / IP 

        str = hostname + ' / ' + ip
        if (draw.textsize(str)[0] > device.width):
            if (frame % 2):
                str = ip
            else:
                str = hostname
        draw.text((x, y), str, fill="white")
        y += draw.textsize(str)[1] + 1

        # Line 2: loadavg - minigraph

        str = getloadavg()
        draw.text((x, y), str, fill="white")
        y += draw.textsize(str)[1] + 1
        cpugraph(draw, device.width - hist_size - 3, y - 10, 10)

        # Line 3: Rx - minigraph

        rx = getrxspeed()
        str = 'Rx: ' + pretty_speed(rx)
        draw.text((x, y), str, fill="white")
        y += draw.textsize(str)[1] + 1
        #rxgraph(draw, device.width - hist_size - 3, y - 10, 10)

    time.sleep(1)
    frame+=1
    if (frame > 256):
        frame = 0

