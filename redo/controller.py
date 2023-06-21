from time import sleep
from machine import Pin,PWM,ADC
from neopixel import NeoPixel


def display(*args):
    print(tuple(args))

class Voltmeter:
    def __init__(self):
        self.volt = 0
        self.voltages = []
        self.max_ac = 0
        self.dc_offset = 0

        self.microphone = ADC(Pin(34))
        self.microphone.atten(ADC.ATTN_11DB)

    def do(self):
        self.volt = self.microphone.read()
        self.voltages.append(self.volt)
        if len(self.voltages)>100:
            self.voltages.pop(0)

        self.dc_offset = sum(self.voltages)/len(self.voltages)
        self.max_ac = max(self.voltages)-self.dc_offset

    def ac_applitude_normalized(self):
        last_few = self.voltages[-5:-1]
        average = sum(last_few)/len(last_few)
        ac_current = average - self.dc_offset
        ac_clip = max(ac_current,0)
        volume = ac_clip/self.max_ac
        return volume





class Controller():
    def __init__(self):
        self.servo_0 = PWM(Pin(32), freq = 50)
        self.servo_1 = PWM(Pin(33), freq = 50)

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
        stage = min(int(volume*8),8)
        self.light_leds(stage)

    def volume2servos(self,volume):
        angle = max(min(int(volume*30),30)-10,0)
        self.move_servos(angle)


def main():
    print("start")
    delta_t = 0.01

    voltimeter = Voltmeter()
    controller = Controller()

    run = True
    while run:
        #get sensor input
        voltimeter.do()
        volume = voltimeter.ac_applitude_normalized()

        controller.volume2led(volume)
        controller.volume2servos(volume)

        display(volume)

        #frame rate
        sleep(delta_t)


def test():
    controller = Controller()

    print("start")
    i=0
    while True:
        sleep(0.01)
        i += 0.1
        controller.move_servos(int(i%20))
        display(i%20)
    print("fin")



#test()
main()
