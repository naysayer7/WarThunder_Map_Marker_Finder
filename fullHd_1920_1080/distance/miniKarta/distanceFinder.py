import math
from subprocess import Popen

import cv2
import numpy as np
import pyautogui

MAP_FILE = "map.png"
SCALE_FILE = "scale.txt"
A_LETTER_FILE = "a_letter.png"
E_LETTER_FILE = "e_letter.png"


def checkDistance(modelTank, modelMarker, scale=250):

    ######################################################################
    screen = pyautogui.screenshot(MAP_FILE, region=(1462, 622, 456, 456))
    size = 456
    map = cv2.imread(MAP_FILE)
    ######################################################################

    ######################################################################
    # Определяем позицию танка

    arrowResults = modelTank(screen, size)
    arrowsConfidences = arrowResults.xyxy[0][:, -2].numpy().tolist()

    if arrowsConfidences == []:
        showErrorArrow(scale, screen)
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

    print("Позиция танка", tankPosition)
    ######################################################################

    ######################################################################
    # Определяем позицию желтой метки
    markerResults = modelMarker(screen, size)

    markerConfidences = markerResults.xyxy[0][:, -2].numpy().tolist()
    if markerConfidences == []:
        showErrorMarker(scale, screen)
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

    print("Центр желтого маркера", markerPosition)
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
    print("лев_верх_угол_буква_a", top_left_a)

    eLetter = cv2.imread(E_LETTER_FILE)
    resELetter = cv2.matchTemplate(map, eLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_e = cv2.minMaxLoc(resELetter)
    print("лев_верх_угол_буква_e", top_left_e)
    ###

    line = (top_left_e[1] - top_left_a[1])/4
    if line == 0:
        showAError(scale)
        return
    ######################################################################

    # получаем дистанцию в метрах
    distance = hypotenuse/line*scale
    print("Азимут", angle)
    print("Дистанция", distance)

    command = ["python", 'printResults.py', "true",
               f'{round(distance)}', f'{round(angle,1)}', f'{scale}']
    Popen(command)
    ######################################################################


def showErrorArrow(scale, screen):
    file = open('shit_detection/tank/number.txt', 'r')
    number = file.read()
    if number == "":
        number = "0"
    number = int(number)
    file.close()
    file = open('shit_detection/tank/number.txt', 'w')
    screen.save(f'shit_detection/tank/screen{number}.png')
    number += 1
    file.write(str(number))
    file.close()
    command = ["python", 'printResults.py', "errorArrow", f'{scale}']
    Popen(command)


def showErrorMarker(scale, screen):
    file = open('shit_detection/marker/number.txt', 'r')
    number = file.read()
    if number == "":
        number = "0"
    number = int(number)
    file.close()
    file = open('shit_detection/marker/number.txt', 'w')
    screen.save(f'shit_detection/marker/screen{number}.png')
    number += 1
    file.write(str(number))
    file.close()
    command = ["python", 'printResults.py', "errorMarker", f'{scale}']
    Popen(command)


def showAError(scale):
    command = ["python", 'printResults.py', "AError", f'{scale}']
    Popen(command)
