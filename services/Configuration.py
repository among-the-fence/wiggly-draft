import os

from dotenv import load_dotenv

env = {
    "DEV": {
        "timeout": 10,
        "io_emoji": "<:io:1021872443788370072>",
        "pudge": "<:pudge:1021872278360825906>",
        "hacky_one_click": True,
    },
    "PROD": {
        "timeout": 300,
        "hacky_one_click": False,
    }
}

load_dotenv()

class Configuration:
    @staticmethod
    def get_config(attribute):
        e = os.getenv('ENV')
        e = e if e else 'PROD'
        if attribute in env.get(e):
            return env.get(e)[attribute]
        return os.getenv(attribute)