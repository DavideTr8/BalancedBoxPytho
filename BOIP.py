from parsing import Bomip2dkp, pyo
from lexmin import find_lexmin
from queue import PriorityQueue
from shapes.rectangle import Rectangle
from pathlib import Path
import logging

logging.basicConfig(level=20)

EPS = 0.1  # epsilon for when splitting a rectangle

dataset_path = Path("./BOMIP/Part I- Integer Programs/instances/")
problem = "2DKP"
problem_class = "class A"
instance = "1dat.txt"

solutions_path = Path("./my_solutions")
problem_sol_path = solutions_path / problem / problem_class
problem_sol_path.mkdir(parents=True, exist_ok=True)
instance_sol_path = problem_sol_path / instance

instance_path = dataset_path / problem / problem_class / instance
problem = Bomip2dkp.from_file(instance_path)

# solver_path = "/usr/local/bin/glpsol"
# opt = pyo.SolverFactory("glpk", executable=solver_path)
solver_path = "/home/da_orobix/PycharmProjects/BalancedBoxPython/venv/lib/python3.9/site-packages/pulp/solverdir/cbc/linux/64/cbc"
opt = pyo.SolverFactory("cbc", executable=solver_path)

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
    logging.info(f"Iteration: {iteration}")
    searching_rectangle = pq.get()[1]
    z1, z2 = searching_rectangle.topleft, searching_rectangle.botright

    _, r_b = searching_rectangle.split_horizontally()

    z1_bar = find_lexmin(model, (1, 2), opt, shape=r_b, verbose=False)
    if z1_bar != z2:
        solutions_list.append(z1_bar)
        new_rect = Rectangle(z1_bar, z2)
        pq.put((-new_rect.area, new_rect))

    r_t = Rectangle(z1, (z1_bar[0] - EPS, (z1[1] + z2[1]) / 2))
    z2_bar = find_lexmin(model, (2, 1), opt, shape=r_t, verbose=False)

    if z2_bar != z1:
        solutions_list.append(z2_bar)
        new_rect = Rectangle(z1, z2_bar)
        pq.put((-new_rect.area, new_rect))

    iteration += 1
    if iteration == 2:
        break

# writer = Writer("max", instance_sol_path)
# writer.print_solution(solutions_list)
