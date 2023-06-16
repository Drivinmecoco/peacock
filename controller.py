from time import sleep
from machine import Pin,PWM,ADC
from neopixel import NeoPixel

#formulas
def volume2stage(volume):
    step = 0.2
    stage = min(volume/step,8)
    return stage

def bass2angle(bass):
    y = min(int(bass*90),90)
    return [y,-y]


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
    #volume2LED(volume)
    move_servos(bass2angle(bass))

#microphone
microphone = ADC(Pin(34))
microphone.atten(ADC.ATTN_11DB)
def get_volume():
    volt = microphone.read()
    return volt

#bass
bass = ADC(Pin(39))
bass.atten(ADC.ATTN_11DB)
def get_bass():
    volt = bass.read()
    return volt

def avg(lst,offset,l):
    return sum(
        [abs(lst[i]-offset) for i in range(len(lst)-1,len(lst)-l-1,-1)]
        )/l

def main():
    timer = 0
    FPS = 24

    v_l = 5
    volumes = [2500 for i in range(v_l)]#0.1s
    b_l = 10
    basses = [2500 for i in range(b_l)]#0.1s


    run = True
    while run:
        #get sensor input
        volume = get_volume()
        volumes.append(volume)

        dc_v = sum(volumes)/len(volumes)
        avg_v = avg(volumes,dc_v,v_l)


        bass_volume = get_bass()
        basses.append(bass_volume)
        dc_b = sum(basses)/len(basses)
        avg_b = avg(basses,dc_b,b_l)

        #print(tuple([avg_v,abs(volume-dc_v)]))
        #print(tuple([avg_b,abs(bass_volume-dc_b)]))
        print(tuple([avg_b,avg_v]))

        #if you hear a loud sound activate for at least 2s
        if(avg_v>1):
            timer = 2

        #as long as you heard a sound 2s ago, keep playing
        if timer>0:
            pass
            #frame(avg_v,avg_b)

        #frame rate
        sleep(1/FPS)
        timer -= 1/FPS

main()

"""
def test():
    while True:
        #print(tuple([get_volume()]))
        sleep(0.01)
#test()
"""
