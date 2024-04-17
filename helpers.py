import datetime
#can id 276
class timeClass():
    def __init__(self):
        self.data = bytearray([0b00000000, 0b00010000, 0b00000000, 0b00000000, 0b00000000, 0b00011011,0b00010000])
    def setTime(self, date):
        # Year
        self.data[0] = (self.data[0] & 0b10000000) + ((date.year - 2000) & 0b1111111)
        # Month
        self.data[1] = (self.data[1] & 0b11110000) + ((date.month) & 0b1111)
        # Day
        self.data[2] = (self.data[2] & 0b11100000) + ((date.day) & 0b111111)
        # Hour
        self.data[3] = (self.data[3] & 0b11100000) + ((date.hour) & 0b11111)
        # Minute
        self.data[4] = (self.data[4] & 0b11000000) + ((date.minute) & 0b111111)
    def setShow24HValue(self, val):
        self.data[0] = (self.data[0] & 0b01111111) + (val << 7)
    def getMsgBuf(self):
        return bytearray(self.data)
    def reset(self):
        self.data = bytearray([0b00000000, 0b00010000, 0b00000000, 0b00000000, 0b00000000, 0b00011011,0b00010000])

class displayButtons():
    def __init__(self):
        self.data = bytearray([0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000])
    def setButton(self, buttonID):
        button = int(buttonID['button'])
        # 109 menu
        if button == 109:
            self.data[5] = (self.data[5] & 0b10111111) + (1 << 6)
        # 110 mode
        elif button == 110:
            self.data[1] = (self.data[1] & 0b11101111) + (1 << 4)
        # 101 ok
        elif button == 101:
            self.data[2] = (self.data[2] & 0b10111111) + (1 << 6)
        # 113 esc
        elif button == 113:
            self.data[2] = (self.data[2] & 0b11101111) + (1 << 4)
        # 119 up
        elif button == 119:
            self.data[5] = (self.data[5] & 0b10111111) + (1 << 6)
        # 115 down
        elif button == 115:
            self.data[5] = (self.data[5] & 0b11101111) + (1 << 4)
        # 97 left
        elif button == 97:
            self.data[5] = (self.data[5] & 0b11111110) + (1)
        # 100 right
        elif button == 100:
            self.data[5] = (self.data[5] & 0b11111011) + (1 << 2)
        #201 dark
        elif button == 201:
            self.data[2] = (self.data[2] & 0b11111011) + (1 << 2)
        
    def getMsgBuf(self):
        return bytearray(self.data)
    def reset(self):
        self.data = bytearray([0b00000000,0b00000000,0b00000000,0b00000000,0b00000000,0b00000000])

settime = timeClass()
settime.setTime(datetime.datetime.strptime("18/04/2024, 17:30:00", "%d/%m/%Y, %H:%M:%S"))
print(settime.getMsgBuf())

buttons = displayButtons()
buttons.setButton({"button": 110})
print(buttons.getMsgBuf())