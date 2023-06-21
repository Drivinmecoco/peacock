from time import sleep
from machine import Pin,PWM,ADC
from neopixel import NeoPixel
from math import sin, pi


def plot(*args):
    print(tuple(args))

class Voltmeter:
    def __init__(self):
        self.volt = 0
        self.voltages = [2350 for i in range(5)]
        self.max_ac = 1
        self.dc_offset = 2500
        self.avg = 2500
        self.ac = 0
        self.acs = [0]

        self.microphone = ADC(Pin(39))
        self.microphone.atten(ADC.ATTN_11DB)

        self.count_step = 5
        self.count = 0

    def do(self):
        self.volt = self.microphone.read()
        if self.count%self.count_step == 0:
            self.voltages.append(self.volt)

        self.resize()

        self.dc_offset = max(sum(self.voltages)/len(self.voltages),2200)
        self.ac_applitude()

        self.count+=1

    def ac_normalized(self):
        return max(min(self.ac/self.max_ac,1),0)

    def ac_applitude(self):
        last_few = self.voltages[-20:-1]
        self.avg = sum(last_few)/len(last_few)
        self.ac = abs(self.avg - self.dc_offset)
        self.acs.append(self.ac)
        self.max_ac = max(self.acs+[1000])

    def resize(self):
        if len(self.voltages)>200:
            self.voltages.pop(0)
        if len(self.acs)>200:
            self.acs.pop(0)



class Controller():
    def __init__(self):
        self.servo_0 = PWM(Pin(32), freq = 50)
        self.servo_1 = PWM(Pin(33), freq = 50)

        self.angle = 0
        self.stage = 0

        self.led = NeoPixel(Pin(4),8)

    def move_servos(self,angle):
        self.servo_0.duty(90-angle)
        self.servo_1.duty(angle+30)

    def light_leds(self,stage):
        black = (0,0,0)
        for i in range(8):
            self.led[i] = black

        white = (40,40,40)
        for i in range(0,stage):
            self.led[i] = white
        self.led.write()

    def volume2led(self,volume):
        sensitivity = 1.2

        stage = min(int(volume*8*sensitivity),8)
        self.stage = stage
        self.light_leds(stage)

    def volume2servos(self,volume):
        sensitivity = 1.5

        max_a = 40

        #angle = max(min(int(volume*30*sensitivity),30)-10,0)
        angle = max(min(int(volume*max_a*sensitivity),max_a)-10,0)
        self.angle = angle
        self.move_servos(angle)


def main():
    print("start")
    delta_t = 0.01

    voltmeter = Voltmeter()
    controller = Controller()

    run = True
    while run:
        #get sensor input
        voltmeter.do()
        volume = voltmeter.ac_normalized()

        controller.volume2led(volume)
        controller.volume2servos(volume)

        plot(volume,controller.angle/90,controller.stage/8)

        #frame rate
        sleep(delta_t)


def cycle():
    voltmeter = Voltmeter()
    controller = Controller()
    i=0
    volume = 0

    print("start")
    while True:
        sleep(0.01)
        controller.volume2servos(volume)

        controller.volume2led(volume)
        i += 0.01
        w = 120 #120bpm
        r = 1/60*1.362*pi
        volume = 0.5*sin(w*r*i)+0.5
        plot(volume)

def test():
    voltmeter = Voltmeter()
    controller = Controller()
    i=0
    volume = 0

    print("start")
    while True:
        sleep(0.01)
        controller.volume2servos(volume)

        controller.volume2led(volume)
        i += 0.01
        w = 70/(2*pi)
        volume = 0.5*sin(w*i)+0.5
        plot(volume)


cycle()
#main()
