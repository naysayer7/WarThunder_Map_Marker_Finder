import math

import cv2
import numpy as np
from imagehash import average_hash
from PIL.Image import Image
from printResults import show

MAP_FILE = "map.png"
SCALE_FILE = "scale.txt"
A_LETTER_FILE = "a_letter.png"
E_LETTER_FILE = "e_letter.png"


def get_distance(modelTank, modelMarker, screen: Image, scale=250):
    ######################################################################
    screen.save("map.png")
    size = 456
    ######################################################################
    map = cv2.imread(MAP_FILE)
    ######################################################################
    # Определяем позицию танка

    arrowResults = modelTank(screen, size)
    arrowsConfidences = arrowResults.xyxy[0][:, -2].numpy().tolist()

    if arrowsConfidences == []:
        screen.save(f"shit_detection/A{average_hash(screen)}.png")
        show("Player not found")
        return

    arrowsCoords = arrowResults.xyxy[0][:, :-2].numpy()
    arrowIndex = 0
    arrowMaxConf = 0

    for i in range(len(arrowsConfidences)):
        if arrowsConfidences[i] > arrowMaxConf:
            arrowMaxConf = arrowsConfidences[i]
            arrowIndex = i

    tankArrow = arrowsCoords[arrowIndex]
    tankPosition = ((tankArrow[2]+tankArrow[0])/2,
                    (tankArrow[3]+tankArrow[1])/2)

    print("Tank pos", tankPosition)
    ######################################################################

    ######################################################################
    # Определяем позицию желтой метки
    markerResults = modelMarker(screen, size)

    markerConfidences = markerResults.xyxy[0][:, -2].numpy().tolist()
    if markerConfidences == []:
        screen.save(f"shit_detection/M{average_hash(screen)}.png")
        show("Marker not found")
        return
    markerCoords = markerResults.xyxy[0][:, :-2].numpy()
    markerIndex = 0
    markerMaxConf = 0

    for i in range(len(markerConfidences)):
        if markerConfidences[i] > markerMaxConf:
            markerMaxConf = markerConfidences[i]
            markerIndex = i

    yellowMarker = markerCoords[markerIndex]

    ###
    markerPosition = (
        (yellowMarker[2]+yellowMarker[0])/2, (yellowMarker[3]+yellowMarker[1])/2)
    ###

    print("Marker center", markerPosition)
    ######################################################################

    # катеты по двум точкам
    cathetus1 = abs(tankPosition[0] - markerPosition[0])
    cathetus2 = abs(tankPosition[1] - markerPosition[1])

    ######################################################################
    # дистанция между двумя точками в пикселях
    hypotenuse = np.hypot(cathetus1, cathetus2)
    ######################################################################

    angle = 0

    if cathetus1 == 0:  # обходим деление на ноль
        angle = 90  # угол между двумя катетами
    else:
        angle = math.degrees(math.atan(cathetus2/cathetus1))  # тот же угол

    ######################################################################
    # получаем азимут
    if markerPosition[0] >= tankPosition[0] and markerPosition[1] <= tankPosition[1]:

        angle = 90-angle

    elif markerPosition[0] >= tankPosition[0] and markerPosition[1] > tankPosition[1]:

        angle = 90+angle

    elif markerPosition[0] < tankPosition[0] and markerPosition[1] >= tankPosition[1]:

        angle = 270-angle

    elif markerPosition[0] < tankPosition[0] and markerPosition[1] < tankPosition[1]:

        angle = 270+angle

    # азимут найден
    ######################################################################

    ######################################################################
    # определяем длину единичного отрезка в пикселях
    # по сути тот отрезок, что улитка на миникарте помечает
    # но он всегда разный, поэтому я получил его из
    # взаимного расположения букв по краям миникарты

    # буква A и буква E

    aLetter = cv2.imread(A_LETTER_FILE)
    resALetter = cv2.matchTemplate(map, aLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_a = cv2.minMaxLoc(resALetter)
    print("top_left_a", top_left_a)

    eLetter = cv2.imread(E_LETTER_FILE)
    resELetter = cv2.matchTemplate(map, eLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_e = cv2.minMaxLoc(resELetter)
    print("top_left_e", top_left_e)
    ###

    line = (top_left_e[1] - top_left_a[1])/4
    if line == 0:
        show("A E collide")
        return
    ######################################################################

    # получаем дистанцию в метрах
    distance = hypotenuse/line*scale
    print("Azimuth", angle)
    print("Distance", distance)

    show(f"{round(distance)}\n{round(angle, 1)}")
    ######################################################################
