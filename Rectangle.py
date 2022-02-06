class Rectangle:
    def __init__(self, topleft: tuple[float], botright:tuple[float]):
        self.topleft = topleft
        self.botright = botright

    def __lt__(self, other):
        return self.area < other.area

    def split_horizontally(self):
        midpoint = (self.topleft[1] + self.botright[1])/2
        return (
            Rectangle(self.topleft, (self.botright[0], midpoint)),
            Rectangle((self.topleft[0], midpoint), self.botright),
        )

    @property
    def area(self):
        x1 = self.topleft[0]
        y1 = self.topleft[1]

        x2 = self.botright[0]
        y2 = self.botright[1]

        return (x2 - x1) * (y1 - y2)

if __name__=="__main__":
    a = Rectangle((2, 3), (5, 1))
    print(a.area)

    b, c = a.split_horizontally()
    print(b.area, c.area)