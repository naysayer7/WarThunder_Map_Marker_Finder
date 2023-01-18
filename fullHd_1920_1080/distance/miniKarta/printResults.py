import time
import traceback

from RTSSSharedMemory import RTSSSharedMemory


def print_RTSS(rtss: RTSSSharedMemory, text: str):
    rtss.update_OSD(text.encode("ascii"))


def show(message: str):
    try:
        rtss = RTSSSharedMemory("RTSSwtmmf")

        print_RTSS(rtss, message)

        time.sleep(7)
        rtss.close()

    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.write(str(e))
        file.close()
