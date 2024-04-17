from collections import OrderedDict

CONST_UP_ARROW    = 119  # w
CONST_DOWN_ARROW  = 115  # s
CONST_LEFT_ARROW  = 97   # a
CONST_RIGHT_ARROW = 100  # d
CONST_ESC_BUTTON  = 113  # q
CONST_OK_BUTTON   = 101  # e
CONST_MENU_BUTTON = 109  # m
CONST_MODE_BUTTON = 110  # n
CONST_TRIP_BUTTON = 108  # n
CONST_CAN_RADIO_MENUBUTTONS = [CONST_UP_ARROW, CONST_DOWN_ARROW, CONST_LEFT_ARROW, CONST_RIGHT_ARROW,
                               CONST_ESC_BUTTON, CONST_OK_BUTTON, CONST_MENU_BUTTON, CONST_MODE_BUTTON,
                               CONST_TRIP_BUTTON]

if not hasattr(int, "__dict__"):
    print("SKIP")
    raise SystemExit

class CanArrowsOnRadioStruct:
    def __init__(self):
        self._reserved0 = 0
        self.up = 0
        self._reserved1 = 0
        self.down = 0
        self._reserved2 = 0
        self.right = 0
        self._reserved3 = 0
        self.left = 0

class CanMenuButtonStruct:
    def __init__(self):
        self._reserved0 = 0
        self.menu = 0
        self._reserved1 = 0
        self.phone = 0
        self._reserved2 = 0
        self._reserved3 = 0
        self.aircon = 0
        self._reserved4 = 0

class CanEscOkButtonStruct:
    def __init__(self):
        self._reserved0 = 0
        self.ok = 0
        self._reserved1 = 0
        self.esc = 0
        self._reserved2 = 0
        self.dark = 0
        self._reserved3 = 0
        self._reserved4 = 0

class CanModeButtonStruct:
    def __init__(self):
        self._reserved0 = 0
        self.mode = 0
        self._reserved1 = 0
        self.trip = 0
        self._reserved2 = 0
        self._reserved3 = 0
        self._reserved4 = 0
        self.audio = 0

class CanMenuStruct:
    def __init__(self):
        self.MenuField = CanMenuButtonStruct()
        self.ModeField = CanModeButtonStruct()
        self.EscOkField = CanEscOkButtonStruct()
        self.byte4 = 0
        self.byte5 = 0
        self.ArrowsField = CanArrowsOnRadioStruct()

class CanMenuPacket:
    def __init__(self):
        self.data = CanMenuStruct()

CONST_CAN_RADIO_MENUBUTTONS = [CONST_UP_ARROW, CONST_DOWN_ARROW, CONST_LEFT_ARROW, CONST_RIGHT_ARROW,
                               CONST_ESC_BUTTON, CONST_OK_BUTTON, CONST_MENU_BUTTON, CONST_MODE_BUTTON,
                               CONST_TRIP_BUTTON]

class CanRadioButtonPacketSender:

    def SendButtonCode(self, button):
        buttonId = int(button['button'])
        print(f"Button ID: {buttonId}")
        generator = PacketGenerator()
        if buttonId == CONST_UP_ARROW:
            generator.packet.data.ArrowsField.up = 1
        elif buttonId == CONST_DOWN_ARROW:
            generator.packet.data.ArrowsField.down = 1
        elif buttonId == CONST_LEFT_ARROW:
            generator.packet.data.ArrowsField.left = 1
        elif buttonId == CONST_RIGHT_ARROW:
            generator.packet.data.ArrowsField.right = 1
        elif buttonId == CONST_ESC_BUTTON:
            generator.packet.data.EscOkField.esc = 1
        elif buttonId == CONST_OK_BUTTON:
            generator.packet.data.EscOkField.ok = 1
        elif buttonId == CONST_MENU_BUTTON:
            generator.packet.data.MenuField.menu = 1
        elif buttonId == CONST_MODE_BUTTON:
            generator.packet.data.ModeField.mode = 1
        elif buttonId == CONST_TRIP_BUTTON:
            generator.packet.data.ModeField.trip = 1
        else:
            print("Invalid button ID")
            return
        serializedPacket = generator.serialize()
        print(serializedPacket)
class PacketGenerator:
    def __init__(self):
        self.packet = CanMenuPacket()

    def serialize(self):
        serialized_packet = bytearray()
        serialized_packet.append(self.serialize_struct(self.packet.data.MenuField))
        serialized_packet.append(self.serialize_struct(self.packet.data.ModeField))
        serialized_packet.append(self.serialize_struct(self.packet.data.EscOkField))
        serialized_packet.append(self.packet.data.byte4)
        serialized_packet.append(self.packet.data.byte5)
        serialized_packet.append(self.serialize_struct(self.packet.data.ArrowsField))
        return serialized_packet

    def serialize_struct(self, struct):
        # Iterate through the struct, and turn all ones and zeros ( bits ) into a byte
        byte = 0
        for key in struct.__dict__:
            byte = byte << 1
            byte = byte | struct.__dict__[key]
        print(struct.__dict__)
        byte = byte & 0xFF
        return byte
        
    

sender = CanRadioButtonPacketSender()
sender.SendButtonCode({"button": 113})