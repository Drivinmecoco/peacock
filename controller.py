from time import sleep
from machine import Pin,PWM
from neopixel import NeoPixel

#formulas
def volume2stage(volume):
    step = 1
    stage = min(volume/step,8)
    return stage

def bass2angle(bass):
    y = min(int(bass*0.5),90)
    return [y,y]


#apply calculated angles to servos
servo_0 = PWM(Pin(32), freq = 50)
servo_1 = PWM(Pin(33), freq = 50)
def move_servos(angles):
    servo_0.duty(angles[0])
    servo_1.duty(angles[1])

#applies calculated light stage to leds
leds = NeoPixel(Pin(4),8)
def light_leds(stage):
    white = (255,255,255)
    for i in range(0,stage):
        leds[i] = white
    leds.write()

#what to do each frame
def frame(volume,bass):
    volume2LED(volume)
    move_servos(bass2angle(bass))

#microphone
microphone = Pin(34, Pin.IN)
def get_volume():
    return microphone.value()

#bass
bass_pin = Pin(35, Pin.IN)
def get_bass():
    return bass_pin.value()

def main():
    timer = 0
    FPS = 5
    min_volume = 1
    bass = 0
    volume = 0
    run = True

    while run:
        #get sensor input
        volume = get_volume()
        bass = get_bass()

        #if you hear a loud sound activate for at least 2s
        if(volume>min_volume):
            timer = 2

        #as long as you heard a sound 2s ago, keep playing
        if timer>0:
            frame(volume,bass)

        #frame rate
        sleep(1/FPS)
        timer -= 1/FPS

main()
