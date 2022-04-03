from shapes.shapee import Shape
import math
from shapes.Point import Point


class Rectangle(Shape):
    def __init__(
        self,
        topleft: Point = Point((-math.inf, math.inf)),
        botright: Point = Point((math.inf, -math.inf)),
    ):
        super().__init__(topleft, botright)

    def __lt__(self, other):
        return self.area < other.area

    @property
    def area(self):
        x1 = self.topleft[0]
        y1 = self.topleft[1]

        x2 = self.botright[0]
        y2 = self.botright[1]

        return (x2 - x1) * (y1 - y2)
