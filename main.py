from phew import logging, server, access_point, dns
from phew.template import render_template
from phew.server import redirect
import time
from src import (
    CAN,
    CAN_CLOCK,
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
    CAN_SPEED,
    ERROR,
)

from src import SPIESP32 as SPI
from src import CANFrame
from helpers import (
    timeClass,
    displayButtons,
)
import asyncio
import datetime

DOMAIN = "Peugeot307cc"
can = CAN(SPI(cs=28))


#Parktronic Messsage
#Canbus ID: 0x0E1
#Data Length: 7 Bytes
# 2: Right chan, Left chan, Rear(0), Front(0) channels, Sound enabled
# 3: 00 - 111111 silence, 000000 continuosly beep
# 4: 3 bytes left rear, (011 - 0, 010 - 1, 001 - 2, 000 - 3). 5 bytes rear center ( 000xx - 4, 001xx - 3, 010xx - 3, 011xx - 2, 100xx - 2, 101x - 1, 110xx - 1, 111xx - 0 )
# 5: 3 bytes right rear, 5 bytes front left
# 6: 3 bytes front center, 3 bytes front right, 1 byte Show parktronic window.
# 7: 02 when no sensors, ign off, C2 when no sensors, ign on
#Example Data: 0x00 0xF0 

# 109 menu
menu = CANFrame(can_id=0x3E5, data=b"\x40\x00\x00\x00\x00\x00")
# 108 trip
trip = CANFrame(can_id=0x3E5, data=b"\x00\x40\x00\x00\x00\x00")
# 110 mode
mode = CANFrame(can_id=0x3E5, data=b"\x00\x10\x00\x00\x00\x00")
# 101 ok 
ok = CANFrame(can_id=0x3E5, data=b"\x00\x00\x40\x00\x00\x00")
# 113 esc
esc = CANFrame(can_id=0x3E5, data=b"\x00\x00\x10\x00\x00\x00")
# 119 up
up = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x40")
# 115 down
down = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x10")
# 97 left
left = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x01")
# 100 right
right = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x04")

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
    
@server.route("/")
def index(req):
    if req.method == "GET":
        logging.debug("GET /")
        return render_template("index.html")
    
@server.route("/rest/button", methods=["POST"])
def button(req):
    if req.method == "POST":
        logging.debug(f"POST /rest/button [{req.data}]")
        #sender = CanRadioButtonPacketSender()
        #print(sender.GetButtonCode(req.data))
        #can.sendMessage(sender.GetButtonCode(req.data))
        buttons = displayButtons()
        buttons.setButton(req.data)
        can.sendMessage(CANFrame(can_id=0x3E5, data=buttons.getMsgBuf()))
        buttons.reset()
        return redirect("/")
    
@server.route("/rest/time", methods=["POST"])
def time(req):
    if req.method == "POST":
        logging.debug(f"POST /rest/time [{req.data}]")
        settime = timeClass()
        settime.setTime(datetime.datetime.strptime(req.data["time"], "%d/%m/%Y, %H:%M:%S"))
        can.sendMessage(CANFrame(can_id=0x276, data=settime.getMsgBuf()))
        settime.reset()
        return redirect("/")

# microsoft windows redirects
@server.route("/ncsi.txt", methods=["GET"])
def hotspot(request):
    print(request)
    print("ncsi.txt")
    return "", 200


@server.route("/connecttest.txt", methods=["GET"])
def hotspot(request):
    print(request)
    print("connecttest.txt")
    return "", 200


@server.route("/redirect", methods=["GET"])
def hotspot(request):
    print(request)
    print("****************ms redir*********************")
    return redirect(f"http://{DOMAIN}/", 302)

# android redirects
@server.route("/generate_204", methods=["GET"])
def hotspot(request):
    print(request)
    print("******generate_204********")
    return redirect(f"http://{DOMAIN}/", 302)

# apple redir
@server.route("/hotspot-detect.html", methods=["GET"])
def hotspot(request):
    print(request)
    """ Redirect to the Index Page """
    return render_template("index.html")


@server.catchall()
def catch_all(request):
    print("***************CATCHALL***********************\n" + str(request))
    return redirect("http://" + DOMAIN + "/")


async def main():

    # Configuration
    if can.reset() != ERROR.ERROR_OK:
        print("Can not reset for MCP2515")
        return
    if can.setBitrate(CAN_SPEED.CAN_125KBPS, CAN_CLOCK.MCP_16MHZ) != ERROR.ERROR_OK:
        print("Can not set bitrate for MCP2515")
        return
    if can.setNormalMode() != ERROR.ERROR_OK:
        print("Can not set normal mode for MCP2515")
        return
    else:
        logging.info("CAN initialized")

    ap = access_point(DOMAIN)
    ip = ap.ifconfig()[0]
    logging.info(f"starting DNS Serv on {ip}")
    asyncio.create_task(CANSendTaskFunction())
    dns.run_catchall(ip)
    server.run()
    logging.info("webserv started")


def listenCan():
    end_time, n = time.ticks_add(time.ticks_ms(), 1000), -1
    while True:
        error, iframe = can.readMessage()
        if error == ERROR.ERROR_OK:
            logging.debug("RX {}".format(iframe))

async def CANSendTaskFunction():
    while True:
        data = b"\x00\x00\x00\x00\x00\x00"
        err = can.sendMessage(CANFrame(can_id=0x3E5, data=data))
        if err == ERROR.ERROR_OK:
            logging.debug("Message sent")
        else:
            logging.error("Error sending message")
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down")
        pass