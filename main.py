from parsing import Bomip2dkp, Path, pyo
from lexmin import find_lexmin
from queue import PriorityQueue
from Rectangle import Rectangle
import logging

logging.basicConfig(level=20)

EPS = 1  # epsilon for when splitting a rectangle

dataset_path = Path("./BOMIP/Part I- Integer Programs/instances/")
problem = "2DKP"
problem_class = "class A"
instance = "1dat.txt"

instance_path = dataset_path / problem / problem_class / instance
problem = Bomip2dkp.from_file(instance_path)

solver_path = "/usr/local/bin/glpsol"
opt = pyo.SolverFactory("glpk", executable=solver_path)

model = problem.to_pyomo()

z_T = find_lexmin(
    model, (1, 2), opt
)  # (pyo.value(model.objective1), pyo.value(model.objective2))
z_B = find_lexmin(
    model, (2, 1), opt
)  # (pyo.value(model.objective1), pyo.value(model.objective2))

solutions_list = [z_T, z_B]
r = Rectangle(z_T, z_B)
pq = PriorityQueue()
pq.put((-r.area, r))

iteration = 1
while not pq.empty():
    print(f"Iteration: {iteration}")
    searching_rectangle = pq.get()[1]
    _, r_b = searching_rectangle.split_horizontally()
    z1, z2 = r_b.topleft, r_b.botright
    z1_bar = find_lexmin(model, (1, 2), opt, rectangle=r_b, verbose=True)
    if z1_bar != z2:
        solutions_list.append(z1_bar)
        new_rect = Rectangle(z1_bar, z2)
        pq.put((-new_rect.area, new_rect))

    r_t = Rectangle(z1, (z1_bar[0] - EPS, (z1[1] + z2[1]) / 2))
    z2_bar = find_lexmin(model, (2, 1), opt, rectangle=r_t, verbose=True)

    if z2_bar != z1:
        solutions_list.append(z2_bar)
        new_rect = Rectangle(z1, z2_bar)
        pq.put((-new_rect.area, new_rect))

    iteration += 1
    if iteration == 5:
        break
