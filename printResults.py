from time import sleep

from config import Config
from RTSS.sharedmemory import ConnectionFailed, SharedMemoryRTSS


def show(message: str):
    conf = Config()

    try:
        rtss = SharedMemoryRTSS("RTSSwtmmf")
        rtss.update_OSD(message.encode("ascii"))
        if float(conf.get("showtime")):
            sleep(float(conf.get("showtime")))
            rtss.update_OSD(b"")
        rtss.close()

    except ConnectionFailed:
        print("Unable to connect to the RTSS")
