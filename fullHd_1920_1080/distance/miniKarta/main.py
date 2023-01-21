import threading
import traceback
from time import sleep

import distanceFinder
import mss
import PIL.Image
import torch
from config import get_conf, write_conf
from dearpygui.dearpygui import *
from PIL.Image import Image
from pynput import keyboard
from RTSSSharedMemory import RTSSSharedMemory


def init_nn():
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

    return modelMarker, modelTank


def take_screenshot(region) -> Image:
    region = [region[0], region[1], region[0] +
              region[2], region[1] + region[3]]

    with mss.mss() as sct:
        sct_image = sct.grab(sct.monitors[1])
        img = PIL.Image.frombytes(
            "RGB", sct_image.size, sct_image.bgra, "raw", "BGRX")

        return img.crop(region)


def default_texture() -> list:
    texture_data = []
    for _ in range(0, 456 * 456):
        texture_data.append(0)  # Red
        texture_data.append(0)  # Green
        texture_data.append(0)  # Blue
        texture_data.append(1)  # Alpha
    return texture_data


def update_texture(img: Image):
    new_texture_data = []
    for i in list(img.getdata()):
        for j in i:
            new_texture_data.append(j/255)
        new_texture_data.append(1)

    set_value("texture_tag", new_texture_data)


def main():
    try:
        modelMarker, modelTank = init_nn()
        # модели нейросетей готовы к работе

        conf = get_conf()

        scale = 250

        def scale_callback(sender, app_data):
            nonlocal scale
            scale = app_data

        def on_distance():
            sleep(float(conf["Delay"]))
            screen = take_screenshot((1462, 622, 456, 456))
            update_texture(screen)
            threading.Thread(target=distanceFinder.get_distance,
                             args=(modelTank, modelMarker, screen, scale)).start()

        def save_conf(sender, app_data):
            new_conf = {}
            new_conf["Delay"] = round(get_value("delay_input"), 3)
            new_conf["Showtime"] = round(get_value("showtime_input"), 3)
            new_conf["Hotkey"] = get_value("hotkey_input")
            write_conf(new_conf)

        keyboard.GlobalHotKeys({"`": on_distance}).start()

        create_context()
        with texture_registry(show=False):
            add_dynamic_texture(width=456, height=456,
                                default_value=default_texture(), tag="texture_tag")

        with window(tag="primary_window"):
            with tab_bar():
                with tab(label="main"):
                    add_input_int(label="Scale", default_value=scale,
                                  callback=scale_callback)
                    add_image("texture_tag")

                with tab(label="preferences"):
                    add_input_float(label="delay, s",
                                    default_value=float(conf["Delay"]),
                                    tag="delay_input")

                    add_input_float(label="showtime, s",
                                    default_value=float(conf["Showtime"]),
                                    tag="showtime_input")

                    add_input_text(label="hotkey",
                                   default_value=conf["Hotkey"],
                                   tag="hotkey_input")

                    add_button(label="save", width=456, callback=save_conf)

        create_viewport(title="WT Marker Rangefinder", width=486, height=600)
        setup_dearpygui()
        show_viewport()
        set_primary_window("primary_window", True)
        start_dearpygui()
        destroy_context()

        rtss = RTSSSharedMemory("RTSSwtmmf")
        rtss.release_OSD()
        rtss.close()

    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.write(str(e))
        file.close()


if __name__ == "__main__":
    main()
