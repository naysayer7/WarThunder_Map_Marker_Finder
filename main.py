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

# [x, y, sizeReal, size]
RESOLUTIONS = {'1366x768': [1034, 436, 329, 329],
               '1920x1080': [1462, 622, 456, 456],
               '2560x1440': [1952, 832, 605, 465],
               '3840x2160': [2940, 1260, 900, 480],
               '5120x2280': [3924, 1684, 1196, 460], }


def init_models():
    model = torch.hub.load("./yolo5", "custom",
                           "./yolo5/best.onnx", source="local")

    return model


def take_screenshot(region) -> Image:
    region = [region[0], region[1], region[0] +
              region[2], region[1] + region[3]]

    with mss.mss() as sct:
        sct_image = sct.grab(sct.monitors[1])
        img = PIL.Image.frombytes(
            "RGB", sct_image.size, sct_image.bgra, "raw", "BGRX")

        return img.crop(region)


def default_texture(size: int) -> list:
    texture_data = []
    for _ in range(0, size**2):
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
        model = init_models()
        print("Models initialized")

        conf = Config()

        screen_x, screen_y, screen_size, to_size = RESOLUTIONS[conf.get(
            "resolution")]
        screen_region = (
            screen_x, screen_y, screen_size, screen_size)

        scale = 250

        def scale_callback(sender, app_data):
            nonlocal scale
            scale = app_data

        def on_distance():
            sleep(float(conf.get("delay")))
            screen = take_screenshot(screen_region)
            update_texture(screen)

            threading.Thread(target=distanceFinder.get_distance,
                             args=(model, screen, scale, to_size, conf.get("resolution"))).start()

        def save_conf(sender, app_data):
            conf = Config()
            conf.set("Delay", round(get_value("delay_input"), 3))
            conf.set("Showtime", round(get_value("showtime_input"), 3))
            conf.set("Hotkey", get_value("hotkey_input"))
            conf.set("Resolution", get_value("resolution_list"))
            conf.save()

        keyboard.GlobalHotKeys({conf.get("hotkey"): on_distance}).start()

        create_context()
        with texture_registry(show=False):
            add_dynamic_texture(width=screen_size, height=screen_size,
                                default_value=default_texture(screen_size), tag="texture_tag")

        with window(tag="primary_window"):
            with tab_bar():
                with tab(label="main"):
                    add_input_int(label="Scale", default_value=scale,
                                  callback=scale_callback)
                    add_image("texture_tag")

                with tab(label="preferences"):
                    add_input_float(label="delay, s",
                                    default_value=float(conf.get("delay")),
                                    tag="delay_input")

                    add_input_float(label="showtime, s",
                                    default_value=float(conf.get("showtime")),
                                    tag="showtime_input")

                    add_input_text(label="hotkey",
                                   default_value=conf.get("hotkey"),
                                   tag="hotkey_input")

                    add_combo(label="resolution*",
                              items=list(RESOLUTIONS.keys()),
                              default_value=conf.get("resolution"),
                              tag="resolution_list")

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
