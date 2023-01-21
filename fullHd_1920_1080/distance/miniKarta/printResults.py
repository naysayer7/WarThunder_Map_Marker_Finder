from time import sleep

from config import get_conf
from RTSSSharedMemory import ConnectionFailed, RTSSSharedMemory

CONFIG_FILE = "prefs.cfg"


def show(message: str):
    conf = get_conf()

    try:
        rtss = RTSSSharedMemory("RTSSwtmmf")
        rtss.update_OSD(message.encode("ascii"))
        if float(conf["Showtime"]):
            sleep(float(conf["Showtime"]))
            rtss.update_OSD(b"")
        rtss.close()

    except ConnectionFailed:
        print("Unable to connect to the RTSS")
