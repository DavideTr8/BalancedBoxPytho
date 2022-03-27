from parsing import Bomip2C, Bomip2buflp, pyo
from lexmin import find_lexmin, weighted_sum, line_detector
from queue import PriorityQueue
from shapes.rectangle import Rectangle
from shapes.triangle import Triangle
from pathlib import Path
import logging
from utils import dist, SelfOrderingDict
from printer import Writer

import os


logging.basicConfig(level=20)

EPS = float(
    os.getenv("EPS_SPLIT", default=0.001)
)  # epsilon for when splitting a rectangle
DATASET_PATH = Path(
    os.getenv(
        "DATASET_PATH", default="./BOMIP/Part II- Mixed Integer Programs/instances/"
    )
)
SOLUTIONS_PATH = Path(os.getenv("SOLUTIONS_PATH", default="./my_solutions"))


def main(problem, problem_class, instance):
    solutions_path = Path("./my_solutions")
    problem_sol_path = Path.cwd() / solutions_path / problem / problem_class
    problem_sol_path.mkdir(parents=True, exist_ok=True)
    instance_sol_path = Path.cwd() / problem_sol_path / instance

    instance_path = Path.cwd() / DATASET_PATH / problem / problem_class / instance
    model = Bomip2C.from_file(instance_path)  # TODO change parser
    if problem == "First problem":
        problem = Bomip2C.from_file(instance_path)
    elif problem == "Second problem (BUFLP)":
        problem = Bomip2buflp.from_file(instance_path)
    else:
        raise ValueError("Wrong value for the instance argument.")
    opt = pyo.SolverFactory(
        "gurobi",
        executable=os.getenv(
            "SOLVER_PATH", default="/opt/gurobi951/linux64/bin/gurobi.sh"
        ),
    )
    opt.options["MIPGap"] = 1e-5

    z_T = find_lexmin(
        model, (1, 2), opt
    )  # (pyo.value(model.objective1), pyo.value(model.objective2))
    z_B = find_lexmin(
        model, (2, 1), opt
    )  # (pyo.value(model.objective1), pyo.value(model.objective2))

    splitting_direction = 0  # 0 horizontal, 1 vertical
    solutions_dict = SelfOrderingDict({z_T: 0, z_B: 0})
    r = Rectangle(z_T, z_B)
    pq = PriorityQueue()
    pq.put((-r.area, r, splitting_direction))

    iteration = 1
    while not pq.empty():
        logging.info(f"Iteration: {iteration}")

        _, searching_shape, splitting_direction = pq.get()
        z1 = searching_shape.topleft
        z2 = searching_shape.botright

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
                    _, t_b = searching_shape.split_horizontally()
                    z1_bar = find_lexmin(model, (1, 2), opt, t_b)
                    if abs(z1_bar[1] - t_b.topleft[1]) < EPS:
                        z2_bar = z1_bar
                    else:
                        t_t = Triangle(z1, (z1_bar[0] - EPS, z1_bar[1]))
                        z2_bar = find_lexmin(
                            model, (2, 1), opt, shape=t_t, verbose=False
                        )

                else:
                    t_t, _ = searching_shape.split_vertically()
                    z2_bar = find_lexmin(model, (2, 1), opt, t_t)

                    if abs(z2_bar[0] - t_t.botright[0]) < EPS:
                        z1_bar == z2_bar
                    else:
                        t_b = Triangle((z2_bar[0], z2_bar[1] - EPS), z2)

                        z1_bar = find_lexmin(
                            model, (1, 2), opt, shape=t_b, verbose=False
                        )

                new_direction = (splitting_direction + 1) % 2

                if dist(z2_bar, searching_shape.topleft) > EPS:
                    rect = Rectangle(searching_shape.topleft, z2_bar)
                    pq.put((-rect.area, rect, new_direction))
                    solutions_dict[z2_bar] = 0

                if dist(z1_bar, searching_shape.botright) > EPS:
                    rect = Rectangle(z1_bar, searching_shape.botright)
                    pq.put((-rect.area, rect, new_direction))
                    solutions_dict[z1_bar] = 0

        iteration += 1

    writer = Writer("max", instance_sol_path)
    writer.print_solution(solutions_dict)
