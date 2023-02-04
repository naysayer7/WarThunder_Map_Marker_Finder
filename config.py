from configparser import ConfigParser

CONFIG_FILE = "prefs.cfg"


class Config(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance.load()
        return cls.instance

    def load(self):
        with open(f"prefs.cfg", "r") as f:
            self._conf = ConfigParser()
            self._conf.read(CONFIG_FILE)
            self._data = self._conf["DEFAULT"]

    def save(self):
        self._conf["DEFAULT"] = self._data
        with open(CONFIG_FILE, "w") as f:
            self._conf.write(f)

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = str(value)
