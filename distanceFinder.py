import math

import cv2
import numpy as np
from imagehash import average_hash
from PIL.Image import Image

from printResults import show_error, show_result

MAP_FILE = "map.png"
SCALE_FILE = "scale.txt"
A_LETTER_FILE = "a_letter.png"
E_LETTER_FILE = "e_letter.png"


def get_distance(model, screen: Image, scale: int, to_size: int = 480, resolution: int = 1):

    sizeK = to_size/screen.width

    screen.save(MAP_FILE)
    map = cv2.imread(MAP_FILE)

    if sizeK != 1:
        screen = screen.resize((to_size, to_size))

    ######################################################################
    # Определяем позицию игрока и метки

    results = model(screen, 480)
    tankArrow = 0
    yellowMarker = 0

    for i in results.xyxy[0]:
        classD = int(i[5])
        if (classD == 0 or classD == 1) and type(tankArrow) is int:
            tankArrow = i.numpy()
        if classD == 2 and type(yellowMarker) is int:
            yellowMarker = i.numpy()

    if type(tankArrow) is int:
        screen.save(f"shit_detection/A{average_hash(screen)}.png")
        show_error("Player not found")
        return

    if type(yellowMarker) is int:
        screen.save(f"shit_detection/M{average_hash(screen)}.png")
        show_error("Marker not found")
        return

    tankPosition = ((tankArrow[2]+tankArrow[0])/2,
                    (tankArrow[3]+tankArrow[1])/2)

    if sizeK != 1:
        tankPosition = (tankPosition[0]/sizeK, tankPosition[1]/sizeK)

    print("Tank:", tankPosition)

    markerPosition = (
        (yellowMarker[2]+yellowMarker[0])/2, (yellowMarker[3]+yellowMarker[1])/2)

    if sizeK != 1:
        markerPosition = (markerPosition[0]/sizeK, markerPosition[1]/sizeK)

    print("Marker:", markerPosition)

    # print(arrowResults.xyxy[0])
    #      xmin    ymin    xmax   ymax  confidence  class    name
    # 0  749.50   43.50  1148.0  704.5    0.874023      0   arrow

    #arrowsConfidences = arrowResults.xyxy[0][:, -2].numpy().tolist()
    #arrowsCoords = arrowResults.xyxy[0][:, :-2].numpy()

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

    objLet = {
        0: [1, 'a'],
        1: [5, 'e'],
        2: [7, 'g']
    }

    aLetter = cv2.imread(f"./data/resolution_{resolution}/aletter.png")
    resALetter = cv2.matchTemplate(map, aLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_a = cv2.minMaxLoc(resALetter)
    print("Top left A:", top_left_a)

    eLetter = cv2.imread(f"./data/resolution_{resolution}/eletter.png")
    resELetter = cv2.matchTemplate(map, eLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_e = cv2.minMaxLoc(resELetter)
    print("Top left E:", top_left_e)

    gLetter = cv2.imread(f"./data/resolution_{resolution}/gletter.png")
    resGLetter = cv2.matchTemplate(map, gLetter, cv2.TM_CCOEFF_NORMED)
    a, b, d, top_left_g = cv2.minMaxLoc(resGLetter)
    print("Top left G:", top_left_g)

    arrOfLetters = [top_left_a, top_left_e, top_left_g]
    centOfLetters = (arrOfLetters[0][0] +
                     arrOfLetters[1][0] + arrOfLetters[2][0])/3
    maxError = 0
    maxIndex = 2
    for i in range(len(arrOfLetters)):
        delta = abs(centOfLetters-arrOfLetters[i][0])
        if delta > maxError:
            maxError = delta
            maxIndex = i
    newArrOfLetters = []
    for i in range(len(arrOfLetters)):
        if i != maxIndex:
            arr = [arrOfLetters[i][1], objLet[i]]
            newArrOfLetters.append(arr)

    ###

    line = abs(newArrOfLetters[0][0]-newArrOfLetters[1][0]) / \
        abs(newArrOfLetters[0][1][0]-newArrOfLetters[1][1][0])
    print(
        f'Used {newArrOfLetters[0][1][1]} and {newArrOfLetters[1][1][1]}')
    if line == 0:
        show_error("Letters collide")
        return
    ######################################################################

    # получаем дистанцию в метрах
    distance = hypotenuse/line*scale
    print("Azimuth", angle)
    print("Distance", distance)

    show_result(distance, angle)
