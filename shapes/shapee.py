import logging
import math
from shapes.Point import Point
from typing import Union


class Shape:
    def __init__(
        self,
        topleft: Union[tuple, Point] = Point((-math.inf, math.inf)),
        botright: Union[tuple, Point] = Point((math.inf, -math.inf)),
    ):
        if isinstance(topleft, tuple):
            topleft = Point(topleft)
        if isinstance(botright, tuple):
            botright = Point(botright)

        if topleft[0] <= botright[0]:
            self.topleft = topleft
            self.botright = botright
        else:
            logging.warning("Topleft and botright were inverted.")
            raise ValueError("Topleft and botright were inverted.")

    def __lt__(self, other):
        return self.area < other.area

    def __eq__(self, other):
        if isinstance(self, type(other)):
            return self.topleft == other.topleft and self.botright == other.botright
        return False

    @property
    def area(self):
        raise NotImplementedError

    @property
    def horizontal_midpoint(self):
        return (self.topleft[0] + self.botright[0]) / 2

    @property
    def vertical_midpoint(self):
        return (self.topleft[1] + self.botright[1]) / 2

    def split_horizontally(self):
        assert not math.isinf(self.topleft[1]), ValueError(
            "Can't find the midpoint of infinity"
        )
        assert not math.isinf(self.botright[1]), ValueError(
            "Can't find the midpoint of infinity"
        )

        return (
            self.__class__(self.topleft, (self.botright[0], self.vertical_midpoint)),
            self.__class__((self.topleft[0], self.vertical_midpoint), self.botright),
        )

    def split_vertically(self):
        assert not math.isinf(self.topleft[1]), ValueError(
            "Can't find the midpoint of infinity"
        )
        assert not math.isinf(self.botright[1]), ValueError(
            "Can't find the midpoint of infinity"
        )

        return (
            self.__class__(self.topleft, (self.horizontal_midpoint, self.botright[1])),
            self.__class__((self.horizontal_midpoint, self.topleft[1]), self.botright),
        )
