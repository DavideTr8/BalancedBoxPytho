from parsing import Bomip2C, pyo
from lexmin import find_lexmin, weighted_sum, line_detector
from queue import PriorityQueue
from shapes.rectangle import Rectangle
from shapes.triangle import Triangle
from pathlib import Path
import logging

logging.basicConfig(level=20)

EPS = 0.1  # epsilon for when splitting a rectangle

dataset_path = Path("./BOMIP/Part II- Mixed Integer Programs/instances/")
problem = "First problem"
problem_class = "C20"
instance = "1dat.txt"

solutions_path = Path("./my_solutions")
problem_sol_path = solutions_path / problem / problem_class
problem_sol_path.mkdir(parents=True, exist_ok=True)
instance_sol_path = problem_sol_path / instance

instance_path = dataset_path / problem / problem_class / instance
model = Bomip2C.from_file(instance_path)  # TODO change parser

# solver_path = "/usr/local/bin/glpsol"
# opt = pyo.SolverFactory("glpk", executable=solver_path)
solver_path = "/home/da_orobix/PycharmProjects/BalancedBoxPython/venv/lib/python3.9/site-packages/pulp/solverdir/cbc/linux/64/cbc"
opt = pyo.SolverFactory("cbc", executable=solver_path)


z_T = find_lexmin(
    model, (1, 2), opt
)  # (pyo.value(model.objective1), pyo.value(model.objective2))
z_B = find_lexmin(
    model, (2, 1), opt
)  # (pyo.value(model.objective1), pyo.value(model.objective2))

splitting_direction = 0  # 0 horizontal, 1 vertical
solutions_dict = {z_T: 0, z_B: 0}
r = Rectangle(z_T, z_B)
pq = PriorityQueue()
pq.put((-r.area, r, splitting_direction))

iteration = 1
while not pq.empty():
    logging.info(f"Iteration: {iteration}")

    _, searching_shape, splitting_direction = pq.get()

    if isinstance(searching_shape, Rectangle):
        z_cap = weighted_sum(model, opt=opt, rectangle=searching_shape)

        for k in range(len(z_cap) - 1):
            triangle = Triangle(z_cap[k], z_cap[k + 1])
            pq.put((-triangle.area, triangle, splitting_direction))
            if k != 0:
                solutions_dict[z_cap[k]] = 0

    else:
        connected = line_detector(model, opt, searching_shape)
        if connected:
            solutions_dict[searching_shape.topleft] = 1

        else:
            if splitting_direction == 0:
                z2_bar, z1_bar = split_triangle_horiz  # TODO
            else:
                z2_bar, z1_bar = split_triangle_vert  # TODO

            new_direction = (splitting_direction + 1) % 2
            if z2_bar != searching_shape.topleft:
                rect = Rectangle(searching_shape.topleft, z2_bar)
                pq.put((-rect.area, rect, new_direction))
                solutions_dict[z2_bar] = 0

            if z1_bar != searching_shape.botright:
                rect = Rectangle(z1_bar, searching_shape.botright)
                pq.put((-rect.area, rect, new_direction))
                solutions_dict[z1_bar] = 0

# writer = Writer("max", instance_sol_path)
# writer.print_solution(solutions_list)
