from machine import Pin, I2C
from time import sleep
from ssd1306 import SSD1306_I2C
import framebuf

oled = None
class Display:
    line = 0
    def __init__(self):
        global oled
        id = 0 
        sda = Pin(16)
        scl = Pin(17)

        i2c = I2C(id=id, scl=scl, sda=sda)

        self.oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
        self.oled.init_display()

    def print(self, text):
        if self.line >=50:
            self.oled.scroll(0,-10)
            self.line = 40
        #while len(text)>16:
        #    if self.line >=50:
        #        self.oled.scroll(0,-10)
        #        self.line = 40

        #    self.oled.text(text[:16], 0, self.line)
        #    text = text[16:]
        #    self.line += 10
        self.oled.text(text, 0, self.line)
        self.oled.show()
        self.line += 10

if __name__=='__main__':
    d = Display()
    d.print('hej1')
    d.print('hej2')
    d.print('hej test long text')
    d.print('hej4')
    d.print('hej5')
    d.print('hej6')
    d.print('hej7');
    d.print('hej8');
    d.print('hej9');
    d.print('1234567890123456789012345678901234567890');
    d.print('1234567890123456789012345678901234567890');
    
    
    