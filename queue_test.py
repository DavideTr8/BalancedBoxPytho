from queue import PriorityQueue

from Rectangle import Rectangle

q = PriorityQueue()

a = Rectangle((2, 3), (1, 5))
b = Rectangle((2, 3), (1, 4))
d = Rectangle((2, 3), (1, 4))

q.put((-a.area, a))
q.put((-b.area, b))
q.put((-d.area, d))

c = q.get()
print(id(b), id(d), id(c))
