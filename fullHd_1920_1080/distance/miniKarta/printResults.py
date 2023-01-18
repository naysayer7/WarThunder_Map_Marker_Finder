import sys
import time
import traceback

from RTSSSharedMemory import RTSSSharedMemory


def print_RTSS(rtss, text):
    rtss.update_OSD(text.encode("ascii"))


try:
    code = sys.argv[1]
    rtss = RTSSSharedMemory("RTSSwtmmf")

    if code == "true":

        distance = sys.argv[2]
        angle = sys.argv[3]
        scale = sys.argv[4]

        print_RTSS(
            rtss, f"Distance: {distance}\nAngle: {angle}\nScale: {scale}")

    elif code == "errorArrow":
        scale = sys.argv[2]
        print_RTSS(rtss, f"Player not found\nScale: {scale}")

    elif code == "errorMarker":
        scale = sys.argv[2]
        print_RTSS(rtss, f"Marker not found\nScale: {scale}")

    elif code == "AError":
        scale = sys.argv[2]
        print_RTSS(rtss, f"A E collide\nScale: {scale}")

    time.sleep(7)
    rtss.close()
    quit()

except Exception as e:
    file = open('error.log', 'a')
    file.write('\n\n')
    traceback.print_exc(file=file, chain=True)
    traceback.print_exc()
    file.write(str(e))
    file.close()
