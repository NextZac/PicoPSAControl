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
import asyncio

DOMAIN = "car.control"
can = CAN(SPI(cs=28))

# 109
menu = CANFrame(can_id=0x3E5, data=b"\x40\x00\x00\x00\x00\x00")
# 108
trip = CANFrame(can_id=0x3E5, data=b"\x00\x40\x00\x00\x00\x00")
# 110
mode = CANFrame(can_id=0x3E5, data=b"\x00\x10\x00\x00\x00\x00")
# 101
ok = CANFrame(can_id=0x3E5, data=b"\x00\x00\x40\x00\x00\x00")
# 113
esc = CANFrame(can_id=0x3E5, data=b"\x00\x00\x10\x00\x00\x00")
# 119
up = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x40")
# 115
down = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x10")
# 97
left = CANFrame(can_id=0x3E5, data=b"\x00\x00\x00\x00\x00\x01")
# 100
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
        sender = CanRadioButtonPacketSender()
        print(sender.GetButtonCode(req.data))
        can.sendMessage(sender.GetButtonCode(req.data))
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