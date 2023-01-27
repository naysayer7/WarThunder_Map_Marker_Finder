import threading
import traceback
from time import sleep

import distanceFinder
import mss
import PIL.Image
import torch
from config import Config
from dearpygui.dearpygui import *
from PIL.Image import Image
from pynput import keyboard
from RTSS.sharedmemory import ConnectionFailed, SharedMemoryRTSS


def init_models():
    # инициализация модели нейросети для поиска танка
    model_tank = torch.hub.load(
        '../yolo5', 'custom', '../yolo5/bestTank.pt', source='local')  # classes="1"

    # инициализация модели нейросети для поиска метки
    model_marker = torch.hub.load(
        '../yolo5', 'custom', '../yolo5/bestMarker.pt', source='local')  # classes="1"

    # перевод моделей в режим процессора
    # только если нет норм видеокарты
    model_tank.cpu()
    model_marker.cpu()

    # настройка модели танка
    model_tank.conf = 0.15  # NMS confidence threshold отсев по точности первый
    # NMS IoU threshold второй, то есть то что больше 45% в теории пройдет
    model_tank.iou = 0.45
    model_tank.agnostic = False  # NMS class-agnostic
    # NMS multiple labels per box несколько лейблов одному объекту
    model_tank.multi_label = False
    # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs
    model_tank.classes = [0, 1]
    # номера каких классов оставить
    model_tank.max_det = 1000  # maximum number of detections per image
    model_tank.amp = False  # Automatic Mixed Precision (AMP) inference

    # настройка модели маркера
    model_marker.conf = 0.15  # NMS confidence threshold отсев по точности первый
    # NMS IoU threshold второй, то есть то что больше 45% в теории пройдет
    model_marker.iou = 0.45
    model_marker.agnostic = False  # NMS class-agnostic
    # NMS multiple labels per box несколько лейблов одному объекту
    model_marker.multi_label = False
    # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs
    model_marker.classes = [0]
    # номера каких классов оставить
    model_marker.max_det = 1000  # maximum number of detections per image
    model_marker.amp = False  # Automatic Mixed Precision (AMP) inference

    return model_marker, model_tank


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
        print("Initializing models")
        model_marker, model_tank = init_models()
        print("Models initialized")

        conf = Config()

        scale = 250

        def scale_callback(sender, app_data):
            nonlocal scale
            scale = app_data

        def on_distance():
            sleep(float(conf.get("Delay")))
            screen = take_screenshot((1462, 622, 456, 456))
            update_texture(screen)
            threading.Thread(target=distanceFinder.get_distance,
                             args=(model_tank, model_marker, screen, scale)).start()

        def save_conf(sender, app_data):
            conf = Config()
            conf.set("Delay", round(get_value("delay_input"), 3))
            conf.set("Showtime", round(get_value("showtime_input"), 3))
            conf.set("Hotkey", get_value("hotkey_input"))
            Config().save()

        keyboard.GlobalHotKeys({conf.get("Hotkey"): on_distance}).start()

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
                                    default_value=float(conf.get("Delay")),
                                    tag="delay_input")

                    add_input_float(label="showtime, s",
                                    default_value=float(conf.get("Showtime")),
                                    tag="showtime_input")

                    add_input_text(label="hotkey",
                                   default_value=conf.get("Hotkey"),
                                   tag="hotkey_input")

                    add_button(label="save", width=456, callback=save_conf)

        create_viewport(title="WT Marker Rangefinder", width=486, height=600)
        setup_dearpygui()
        show_viewport()
        set_primary_window("primary_window", True)
        start_dearpygui()
        destroy_context()

        try:
            rtss = SharedMemoryRTSS("RTSSwtmmf")
            rtss.release_OSD()
            rtss.close()
        except ConnectionFailed:
            pass
    except Exception as e:
        file = open('error.log', 'a')
        file.write('\n\n')
        traceback.print_exc(file=file, chain=True)
        traceback.print_exc()
        file.write(str(e))
        file.close()


if __name__ == "__main__":
    main()
