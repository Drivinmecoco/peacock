from time import sleep
from machine import Pin,PWM,ADC
from neopixel import NeoPixel

#formulas
def volume2stage(volume):
    stage = min(int(volume*8),8)
    return stage

def bass2angle(bass_v):
    angle = max(min(int(bass_v*30),30)-10,0)
    return [angle,angle]


#apply calculated angles to servos
servo_0 = PWM(Pin(32), freq = 50)
servo_1 = PWM(Pin(33), freq = 50)
def move_servos(angles):
    servo_0.duty(90-angles[0])
    servo_1.duty(angles[1]+30)

#applies calculated light stage to leds
leds = NeoPixel(Pin(4),8)
def light_leds(stage):
    black = (0,0,0)
    for i in range(8):
        leds[i] = black

    white = (40,40,40)
    for i in range(0,stage):
        leds[i] = white
    leds.write()

#microphone
microphone = ADC(Pin(34))
microphone.atten(ADC.ATTN_11DB)
def get_volume():
    volt = microphone.read()
    return volt/4100

#bass
bass = ADC(Pin(39))
bass.atten(ADC.ATTN_11DB)
def get_bass():
    volt = bass.read()
    return volt

def avg(lst,offset,l):
    return sum(
        [2*abs(lst[i]-offset) for i in range(len(lst)-1,len(lst)-l-1,-1)]
        )/l

def dc(lst):
    l=min(40,len(lst))
    return sum(
        [lst[i] for i in range(len(lst)-1,len(lst)-l-1,-1)]
        )/l


#what to do each frame
def frame(avg_v,avg_b):
    light_leds(volume2stage(avg_v))
    move_servos(bass2angle(avg_b))


def main():
    timer = 0
    fps = 24

    v_l = 10
    volumes = [0.5 for i in range(v_l)]#0.1s
    #b_l = 10
    #basses = [2500 for i in range(b_l)]#0.1s

    run = True
    while run:
        #get sensor input
        volume = get_volume()
        volumes.append(volume)

        dc_v = dc(volumes)
        avg_v = avg(volumes,dc_v,v_l)


        #bass_volume = get_volume()#get_bass()
        #basses.append(bass_volume)
        #dc_b = dc(basses)
        #avg_b = avg(basses,dc_b,b_l)

        #print(tuple([avg_v,abs(volume-dc_v)]))
        #print(tuple([avg_b,abs(bass_volume-dc_b)]))
        print(tuple([volume,avg_v]))

        #if you hear a loud sound activate for at least 2s
        if avg_v>0:
            timer = 2

        #as long as you heard a sound 2s ago, keep playing
        if timer>0:
            frame(avg_v,avg_v)#avg_b

        if len(volumes)>100:
            volumes.pop(0)
        #if len(basses)>100:
        #    basses.pop(0)

        #frame rate
        sleep(1/fps)
        timer -= 1/fps

main()

def test():
    print("joe")
    i=0
    while True:
        sleep(0.01)
        i += 0.1
        move_servos([int(i%20),int(i%20)])
        print(tuple([i%20]))
    print("fin")
#test()
