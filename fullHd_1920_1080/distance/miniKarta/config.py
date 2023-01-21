from configparser import ConfigParser

CONFIG_FILE = "prefs.cfg"


def get_conf() -> dict:
    conf = ConfigParser()
    conf.read(CONFIG_FILE)
    return conf["DEFAULT"]


def write_conf(new_conf: dict):
    conf = ConfigParser()
    conf["DEFAULT"] = new_conf
    with open(CONFIG_FILE, "w") as f:
        conf.write(f)
