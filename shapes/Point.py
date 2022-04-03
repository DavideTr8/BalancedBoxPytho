class Point:
    precision = 5

    def __init__(self, data):
        self.data = data
        self.rounded_data = (
            round(data[0], self.precision),
            round(data[1], self.precision),
        )

    def __getitem__(self, item):
        return self.data[item]

    def __eq__(self, other):
        return (
            self.rounded_data[0] == other.rounded_data[0]
            and self.rounded_data[1] == other.rounded_data[1]
        )

    def __sub__(self, other):
        if isinstance(other, tuple):
            other = Point(other)
        new_data = (self[0] - other[0], self[1] - other[1])
        return Point(new_data)

    def __repr__(self):
        return str(self.rounded_data)

    def __hash__(self):
        return hash(self.rounded_data)


if __name__ == "__main__":
    a = Point((1, 2))
    b = (0, 1.000001)
    c = Point((1, 1))

    d = a - b
    xd = [a, c]
    print(d in xd)
