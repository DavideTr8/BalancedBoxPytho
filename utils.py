import math
from collections import UserDict

import logging
from colorlog import ColoredFormatter


class SelfOrderingDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.data = {
            k: self.data[k] for k in sorted(self.data.keys(), key=lambda x: x[0])
        }


def dist(z1, z2, name="E"):
    if name == "E":
        return math.sqrt((z1[0] - z2[0]) ** 2 + (z1[1] - z2[1]) ** 2)
    elif name == "M":
        return abs(z1[0] - z2[0]) + abs(z1[1] - z2[1])


def get_logger(
    name: str,
    message_fmt: str = "[%(blue)s%(asctime)s%(reset)s][%(cyan)s%(name)s%(reset)s][%(log_color)s%(levelname)s%(reset)s] - %(message)s",
) -> logging.Logger:
    formatter = ColoredFormatter(
        message_fmt,
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
