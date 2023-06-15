from time import sleep
from machine import Pin
from neopixel import NeoPixel

leds = NeoPixel(Pin(4),8)


def volume2LED(volume):

    white = (255,255,255)
    step = 1

    stage = min(volume/step,7)
    print(volume)
    for i in range(0,stage):
        leds[i] = white
    leds.write()

volume2LED(5)

def main():
    FPS = 5
    min_volume = 50
    bass = 0
    volume = 3
    run = True
    while run:
        volume2LED(volume)
        sleep(1/FPS)


