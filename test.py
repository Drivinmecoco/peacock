# Write your code here :-)
from oled import OLED

oled = OLED()
oled.poweron()
oled.init_display()

oled.draw_text(0,0,"asdlgnaz")
oled.display()
