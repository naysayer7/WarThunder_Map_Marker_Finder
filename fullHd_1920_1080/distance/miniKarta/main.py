import threading
import traceback
from tkinter import *

import distanceFinder
import torch
from pynput import keyboard
from RTSSSharedMemory import RTSSSharedMemory
from scale import scale


def main():
    try:
        print("Neural networks init")

        # инициализация модели нейросети для поиска танка
        modelTank = torch.hub.load(
            '../yolo5', 'custom', '../yolo5/bestTank.pt', source='local')  # classes="1"

        # инициализация модели нейросети для поиска метки
        modelMarker = torch.hub.load(
            '../yolo5', 'custom', '../yolo5/bestMarker.pt', source='local')  # classes="1"

        # перевод моделей в режим процессора
        # только если нет норм видеокарты
        modelTank.cpu()
        modelMarker.cpu()

        # настройка модели танка
        modelTank.conf = 0.15  # NMS confidence threshold отсев по точности первый
        # NMS IoU threshold второй, то есть то что больше 45% в теории пройдет
        modelTank.iou = 0.45
        modelTank.agnostic = False  # NMS class-agnostic
        # NMS multiple labels per box несколько лейблов одному объекту
        modelTank.multi_label = False
        # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs
        modelTank.classes = [0, 1]
        # номера каких классов оставить
        modelTank.max_det = 1000  # maximum number of detections per image
        modelTank.amp = False  # Automatic Mixed Precision (AMP) inference

        # настройка модели маркера
        modelMarker.conf = 0.15  # NMS confidence threshold отсев по точности первый
        # NMS IoU threshold второй, то есть то что больше 45% в теории пройдет
        modelMarker.iou = 0.45
        modelMarker.agnostic = False  # NMS class-agnostic
        # NMS multiple labels per box несколько лейблов одному объекту
        modelMarker.multi_label = False
        # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs
        modelMarker.classes = [0]
        # номера каких классов оставить
        modelMarker.max_det = 1000  # maximum number of detections per image
        modelMarker.amp = False  # Automatic Mixed Precision (AMP) inference

        # модели нейросетей готовы к работе

        def update_scale():
            x = threading.Thread(target=scale)
            x.start()

        def get_scale() -> int:
            with open("scale.txt", "r") as f:
                return int(f.readline())

        def on_distance():
            x = threading.Thread(target=distanceFinder.get_distance,
                                 args=(modelTank, modelMarker, get_scale()))
            x.start()

        def on_quit():
            rtss = RTSSSharedMemory("RTSSwtmmf")
            rtss.release_OSD()
            rtss.close()
            quit()

        print("\nWaiting for a hotkey")

        with keyboard.GlobalHotKeys({"`": on_distance, "<ctrl>+m": update_scale, "<ctrl>+q": on_quit}) as h:
            h.join()

    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.write(str(e))
        file.close()


if __name__ == "__main__":
    main()
