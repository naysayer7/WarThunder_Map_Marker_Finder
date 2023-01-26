from time import sleep

from config import Config
from RTSSSharedMemory import ConnectionFailed, RTSSSharedMemory


def show(message: str):
    conf = Config()

    try:
        rtss = RTSSSharedMemory("RTSSwtmmf")
        rtss.update_OSD(message.encode("ascii"))
        if float(conf.get("Showtime")):
            sleep(float(conf.get("Showtime")))
            rtss.update_OSD(b"")
        rtss.close()

    except ConnectionFailed:
        print("Unable to connect to the RTSS")
