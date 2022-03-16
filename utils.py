import math
from collections import UserDict


class SelfOrderingDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.data = {
            k: self.data[k] for k in sorted(self.data.keys(), key=lambda x: x[0])
        }


def dist(z1, z2):
    return math.sqrt((z1[0] - z2[0]) ** 2 + (z1[1] - z2[1]) ** 2)
