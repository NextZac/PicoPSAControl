import ctypes

canID = ctypes.c_uint16(0x3E5)

# 109
menu = b"\x40\x00\x00\x00\x00\x00"
# 108
trip = b"\x00\x40\x00\x00\x00\x00"
# 110
mode = b"\x00\x10\x00\x00\x00\x00"
# 101
ok = b"\x00\x00\x40\x00\x00\x00"
# 113
esc = b"\x00\x00\x10\x00\x00\x00"
# 119
up = b"\x00\x00\x00\x00\x00\x40"
# 115
down = b"\x00\x00\x00\x00\x00\x10"
# 97
left = b"\x00\x00\x00\x00\x00\x01"
# 100
right = b"\x00\x00\x00\x00\x00\x04"

# Create a class with a function, where i can send a button code and it returns the can bytearray for that button
class CanRadioButtonPacketSender:
    def GetButtonCode(self, button):
        buttonId = int(button['button'])
        print(f"Button ID: {buttonId}")
        if buttonId == 119:
            return up
        elif buttonId == 115:
            return down
        elif buttonId == 97:
            return left
        elif buttonId == 100:
            return right
        elif buttonId == 113:
            return esc
        elif buttonId == 101:
            return ok
        elif buttonId == 109:
            return menu
        elif buttonId == 110:
            return mode
        elif buttonId == 108:
            return trip
        else:
            print("Invalid button ID")
            return
        
sender = CanRadioButtonPacketSender()
print(sender.GetButtonCode({"button": 109}))