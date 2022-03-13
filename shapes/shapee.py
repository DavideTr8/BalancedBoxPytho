import math


class Shape:
    def __init__(
        self,
        topleft: tuple[float] = (-math.inf, math.inf),
        botright: tuple[float] = (math.inf, -math.inf),
    ):
        self.topleft = topleft
        self.botright = botright

    @property
    def area(self):
        raise NotImplementedError

    @property
    def horizontal_midpoint(self):
        return (self.topleft[0] + self.botright[0]) / 2

    @property
    def vertical_midpoint(self):
        return (self.topleft[1] + self.botright[1]) / 2
