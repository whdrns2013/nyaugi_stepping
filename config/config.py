from configparser import ConfigParser

def load_config(path:str):
    config = ConfigParser()
    config.read(path)
    return config

config = load_config("config/config.ini")