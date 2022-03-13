from shapes.shapee import Shape
import math


class Triangle(Shape):
    def __init__(self, topleft, botright):
        super().__init__(topleft, botright)

    @property
    def area(self):
        x1 = self.topleft[0]
        y1 = self.topleft[1]

        x2 = self.botright[0]
        y2 = self.botright[1]

        if any([abs(p) == math.inf for p in [x1, x2, y1, y2]]):
            raise ValueError("Triangle should not be defined for infinite values")

        return (x2 - x1) * (y1 - y2) / 2
