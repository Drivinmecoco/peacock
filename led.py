from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(4), 8) # 8 pixels in strip, Data on Pin 4
np[0] = (0, 255, 0)   	# Bottom pixel is (R, G, B) red intensity 100 max 255
np[1] = (255, 0, 0)	# Green at 1/2 intensity
np[2] = (255, 255, 64)	# Blue at 1/4 intensity
np.write()

