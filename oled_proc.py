#!/usr/bin/python

# Andrew Villeneuve 2019
# Hello World POC for I2C OLED display

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

## Init Device ##

# select i2c/spi and address
serial = i2c(port=1, address=0x3C)

# select driver chip (SSD130X)
device = ssd1306(serial)

## Draw Stuff ##

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 30), "Hello World", fill="white")

