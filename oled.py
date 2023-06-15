'''
# The MIT License (MIT)
#
# Copyright (c) 2014 Kenneth Henderick
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------
# Modified by Peter Cheung, Imperial College London, 21 May 2020
#    ... for use on Heltec Wifi Kit 32 with 0.96" OLED display
#    .....  created for DE1.3 Electronics 1 module

# Usage:
#    oled = OLED()
# Methods:
    oled.clear() - clear display
    oled.write_coammnd(command_byte) - used internally, DO NOT USE
    oled.invert_display(True/False) - true is black on white
    oled.display() - flash display buffer to see new text
    oled.set_pixel(x,y,state) - set pixel on (True) and off (False)
                0, 0 is top right corner
    oled.init_display() - called before use
    oled.poweron()
    oled.poweroff()
    oled.contrast(value=0..255)
    oled.draw_text(x,y,string, size=1, space=1)  0, 0 is top left corner
'''

import machine
import math
import font
import os
import time

# Constants
DISPLAYOFF          = 0xAE
SETCONTRAST         = 0x81
DISPLAYALLON_RESUME = 0xA4
DISPLAYALLON        = 0xA5
NORMALDISPLAY       = 0xA6
INVERTDISPLAY       = 0xA7
DISPLAYON           = 0xAF
SETDISPLAYOFFSET    = 0xD3
SETCOMPINS          = 0xDA
SETVCOMDETECT       = 0xDB
SETDISPLAYCLOCKDIV  = 0xD5
SETPRECHARGE        = 0xD9
SETMULTIPLEX        = 0xA8
SETLOWCOLUMN        = 0x00
SETHIGHCOLUMN       = 0x10
SETSTARTLINE        = 0x40
MEMORYMODE          = 0x20
COLUMNADDR          = 0x21
PAGEADDR            = 0x22
COMSCANINC          = 0xC0
COMSCANDEC          = 0xC8
SEGREMAP            = 0xA0
CHARGEPUMP          = 0x8D
EXTERNALVCC         = 0x10
SWITCHCAPVCC        = 0x20
SETPAGEADDR         = 0xB0
SETCOLADDR_LOW      = 0x00
SETCOLADDR_HIGH     = 0x10
ACTIVATE_SCROLL                      = 0x2F
DEACTIVATE_SCROLL                    = 0x2E
SET_VERTICAL_SCROLL_AREA             = 0xA3
RIGHT_HORIZONTAL_SCROLL              = 0x26
LEFT_HORIZONTAL_SCROLL               = 0x27
VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
VERTICAL_AND_LEFT_HORIZONTAL_SCROLL  = 0x2A

# I2C devices are accessed through a Device ID. This is a 7-bit
# value but is sometimes expressed left-shifted by 1 as an 8-bit value.
# A pin on SSD1306 allows it to respond to ID 0x3C or 0x3D. The board
# I bought from ebay used a 0-ohm resistor to select between "0x78"
# (0x3c << 1) or "0x7a" (0x3d << 1). The default was set to "0x78"
DEVID = 0x3c   # fixed device ID 60

# I2C communication here is either <DEVID> <CTL_CMD> <command byte>
# or <DEVID> <CTL_DAT> <display buffer bytes> <> <> <> <>...
# These two values encode the Co (Continuation) bit as b7 and the
# D/C# (Data/Command Selection) bit as b6.
CTL_CMD = 0x80
CTL_DAT = 0x40

class OLED(object):

  def __init__(self):
    self.external_vcc = False   # no external vcc
    self.height       = 64
    self.pages        = int(self.height / 8)
    self.columns      = 128

    self.res = machine.Pin(16, machine.Pin.OUT, machine.Pin.PULL_DOWN)
    time.sleep_ms(10)
    self.res.off()     # low reset
    time.sleep_ms(10)
    self.res.on()
    self.i2c= machine.I2C(1, scl=machine.Pin(15), sda=machine.Pin(4), freq=400000) # 400kHz
    self.devid = DEVID
    # used to reserve an extra byte in the image buffer AND as a way to
    # infer the interface type
    self.offset = 1
    # I2C command buffer
    self.cbuffer = bytearray(2)
    self.cbuffer[0] = CTL_CMD

  def clear(self):
    self.buffer = bytearray(self.offset + self.pages * self.columns)
    if self.offset == 1:
      self.buffer[0] = CTL_DAT

  def write_command(self, command_byte):
    try:
        self.cbuffer[1] = command_byte
        self.i2c.writeto(self.devid, self.cbuffer)
        time.sleep_ms(10)
    except OSError:
        print("OLED Communication Error")

  def invert_display(self, invert):
    self.write_command(INVERTDISPLAY if invert else NORMALDISPLAY)

  def display(self):
    self.write_command(COLUMNADDR)
    self.write_command(0)
    self.write_command(self.columns - 1)
    self.write_command(PAGEADDR)
    self.write_command(0)
    self.write_command(self.pages - 1)
    self.i2c.writeto(self.devid, self.buffer)

  def set_pixel(self, x, y, state):
    x = max(0, min(x,127))
    y = max(0, min(y,63))

    index = x + (int(y / 8) * self.columns)
    if state:
      self.buffer[self.offset + index] |= (1 << (y & 7)) 
    else:
      self.buffer[self.offset + index] &= ~(1 << (y & 7))

  def init_display(self):
    chargepump = 0x10 if self.external_vcc else 0x14
    precharge  = 0x22 if self.external_vcc else 0xf1
    multiplex  = 0x1f if self.height == 32 else 0x3f
    compins    = 0x02 if self.height == 32 else 0x12
    contrast   = 0xff # 0x8f if self.height == 32 else (0x9f if self.external_vcc else 0x9f)
    data = [DISPLAYOFF,
            SETDISPLAYCLOCKDIV, 0x80,
            SETMULTIPLEX, multiplex,
            SETDISPLAYOFFSET, 0x00,
            SETSTARTLINE | 0x00,
            CHARGEPUMP, chargepump,
            MEMORYMODE, 0x00,
            SEGREMAP | 0x10,
            COMSCANDEC,
            SETCOMPINS, compins,
            SETCONTRAST, contrast,
            SETPRECHARGE, precharge,
            SETVCOMDETECT, 0x40,
            DISPLAYALLON_RESUME,
            NORMALDISPLAY,
            DISPLAYON]
    for item in data:
      self.write_command(item)
    self.clear()
    self.display()

  def poweron(self):
    self.write_command(DISPLAYON)

  def poweroff(self):
    self.write_command(DISPLAYOFF)

  def contrast(self, contrast):
    self.write_command(SETCONTRAST)
    self.write_command(contrast)

  def draw_text(self, x, y, string, size=1, space=1):
    def pixel_x(char_number, char_column, point_row):
      char_offset = x + char_number * size * font.cols + space * char_number
      pixel_offset = char_offset + char_column * size + point_row
      return self.columns - pixel_offset

    def pixel_y(char_row, point_column):
      char_offset = y + char_row * size
      return char_offset + point_column

    def pixel_mask(char, char_column, char_row):
      char_index_offset = ord(char) * font.cols
      return font.bytes[char_index_offset + char_column] >> char_row & 0x1

    pixels = (
      (pixel_x(char_number, char_column, point_row),
       pixel_y(char_row, point_column),
       pixel_mask(char, char_column, char_row))
      for char_number, char in enumerate(string)
      for char_column in range(font.cols)
      for char_row in range(font.rows)
      for point_column in range(size)
      for point_row in range(1, size + 1))

    for pixel in pixels:
      self.set_pixel(*pixel)
      
  def draw_circle(self, x0, y0 ,r, state):
    '''
    draw circle with centre (x0,y0) and radius r
    '''
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    self.set_pixel(x0, y0+r, state)
    self.set_pixel(x0  , y0-r, state)
    self.set_pixel(x0+r, y0  , state)
    self.set_pixel(x0-r, y0  , state)
    while (x<y):
        if (f >= 0):
            y -= 1
            ddF_y += 2
            f += ddF_y
        x +=1
        ddF_x += 2
        f += ddF_x
        self.set_pixel(x0 + x, y0 + y, state)
        self.set_pixel(x0 - x, y0 + y, state)
        self.set_pixel(x0 + x, y0 - y, state)
        self.set_pixel(x0 - x, y0 - y, state)
        self.set_pixel(x0 + y, y0 + x, state)
        self.set_pixel(x0 - y, y0 + x, state)
        self.set_pixel(x0 + y, y0 - x, state)
        self.set_pixel(x0 - y, y0 - x, state)
        
  def draw_square(self,x,y,size, state):
    for i in range(-size,+size):
        for j in range(-size, +size):
            self.set_pixel(x+i,y+j,state)

  def swap(self,x,y,yes):
    if yes:
        return (y,x)
    else:
        return (x,y)

# Draw line using Bresenham's algorithm
  def draw_line(self, xa, ya, xb, yb, state):
    '''
    Draw a line from (xa,ya) to (xb,yb)
    '''
    steep = abs(yb - ya) > abs(xb - xa)
    x0,y0 = self.swap(xa, ya,steep)
    x1,y1 = self.swap(xb, yb,steep)
    yes = x0>x1
    x0,x1 = self.swap(x0, x1, yes)
    y0,y1 = self.swap(y0, y1, yes)
    dx = x1 - x0
    dy = abs(y1 - y0)
    err = dx // 2
    ystep = -1
    if (y0 < y1):
        ystep = 1
    while (x0<=x1):
        if (steep):
            self.set_pixel(y0, x0, state)
        else:
            self.set_pixel(x0, y0, state)
        err -= dy
        if (err < 0):
            y0 += ystep
            err += dx;
        x0+=1


  def line(self,x,y,phi,d, state):
    '''
    Draw a line of lenght d from (x,y) at angle phi in degrees
    '''
    a = math.radians(phi)
    x1 = int(x + d * math.sin(a))
    y1 = int(y + d * math.cos(a))
    self.draw_line(x,y,x1,y1, state)
