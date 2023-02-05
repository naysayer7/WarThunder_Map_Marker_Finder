from ast import literal_eval
from time import sleep

from config import Config
from RTSS.sharedmemory import ConnectionFailed, SharedMemoryRTSS


def show_error(message: str):
    conf = Config()

    try:
        rtss = SharedMemoryRTSS("RTSSwtmmf")

        strOSD = ""
        if rtss.formatTagsSupported:
            strOSD += f"<C0=ff0000>"
            strOSD += f"<C0>{message}<C>"
        else:
            strOSD = "Please update RTSS"
        rtss.update_OSD(strOSD.encode("ascii"))
        if float(conf.get("showtime")):
            sleep(float(conf.get("showtime")))
            rtss.update_OSD(b"")
        rtss.close()
    except ConnectionFailed:
        print("Unable to connect to the RTSS")


def show_result(distance: int, azimuth: int):
    conf = Config()

    try:
        rtss = SharedMemoryRTSS("RTSSwtmmf")

        strOSD = ""
        if rtss.formatTagsSupported:
            ac = tuple(map(int, literal_eval(conf.get("azimuth_color"))[:3]))
            dc = tuple(map(int, literal_eval(conf.get("distance_color"))[:3]))
            strOSD += f"<C0=" + str("%02x%02x%02x" % dc) + ">"
            strOSD += f"<C1=" + str("%02x%02x%02x" % ac) + ">"
            strOSD += f"<C0>{round(distance)}<C>"
            strOSD += f"\n"
            strOSD += f"<C1>{round(azimuth, 1)}<C>"
        else:
            strOSD = "Please update RTSS"

        rtss.update_OSD(strOSD.encode("ascii"))
        if float(conf.get("showtime")):
            sleep(float(conf.get("showtime")))
            rtss.update_OSD(b"")
        rtss.close()

    except ConnectionFailed:
        print("Unable to connect to the RTSS")
