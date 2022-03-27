import os

from parsing import Bomip2dkp, Bomip2ap, pyo
from lexmin import find_lexmin
from queue import PriorityQueue
from shapes.rectangle import Rectangle
from pathlib import Path
import logging
from utils import SelfOrderingDict, dist
from printer import Writer

logging.basicConfig(level=20)

EPS = float(os.getenv("EPS_SPLIT", default=1))  # epsilon for when splitting a rectangle
DIFF_EPS = 0.1
DATASET_PATH = Path(
    os.getenv("DATASET_PATH", default="./BOMIP/Part I- Integer Programs/instances/")
)
SOLUTIONS_PATH = Path(os.getenv("SOLUTIONS_PATH", default="./my_solutions"))


def main(problem, problem_class, instance):

    problem_sol_path = Path.cwd() / SOLUTIONS_PATH / problem / problem_class
    problem_sol_path.mkdir(parents=True, exist_ok=True)
    instance_sol_path = Path.cwd() / problem_sol_path / instance

    instance_path = Path.cwd() / DATASET_PATH / problem / problem_class / instance

    if problem == "2DKP":
        problem = Bomip2dkp.from_file(instance_path)
    elif problem == "AP":
        problem = Bomip2ap.from_file(instance_path)
    else:
        raise ValueError("Wrong value for the instance argument.")

    opt = pyo.SolverFactory(
        "gurobi",
        executable=os.getenv(
            "SOLVER_PATH", default="/opt/gurobi951/linux64/bin/gurobi.sh"
        ),
    )

    model = problem.to_pyomo()

    z_T = find_lexmin(
        model, (1, 2), opt
    )  # (pyo.value(model.objective1), pyo.value(model.objective2))
    z_B = find_lexmin(
        model, (2, 1), opt
    )  # (pyo.value(model.objective1), pyo.value(model.objective2))

    solutions_dict = SelfOrderingDict({z_T: 0, z_B: 0})
    r = Rectangle(z_T, z_B)
    pq = PriorityQueue()
    pq.put((-r.area, r))

    iteration = 1
    while not pq.empty():
        logging.info(f"Iteration: {iteration}")
        searching_rectangle = pq.get()[1]
        z1, z2 = searching_rectangle.topleft, searching_rectangle.botright

        _, r_b = searching_rectangle.split_horizontally()

        try:
            z1_bar = find_lexmin(model, (1, 2), opt, shape=r_b, verbose=False)
            if dist(z1_bar, z2) > DIFF_EPS:
                solutions_dict[z1_bar] = 0
                new_rect = Rectangle(z1_bar, z2)
                if new_rect.area >= EPS:
                    pq.put((-new_rect.area, new_rect))

            r_t = Rectangle(z1, (z1_bar[0] - EPS, (z1[1] + z2[1]) / 2))
            z2_bar = find_lexmin(model, (2, 1), opt, shape=r_t, verbose=False)

            if dist(z2_bar, z1) > DIFF_EPS:
                solutions_dict[z2_bar] = 0
                new_rect = Rectangle(z1, z2_bar)
                if new_rect.area >= EPS:
                    pq.put((-new_rect.area, new_rect))
        except ValueError:
            logging.warning("Solution not found during this iteration")
        iteration += 1

    writer = Writer("max", instance_sol_path)
    writer.print_solution(solutions_dict)
