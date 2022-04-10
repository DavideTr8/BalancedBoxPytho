from parsing import Bomip2C, Bomip2buflp, pyo
from lexmin import find_lexmin, weighted_sum, line_detector
from queue import PriorityQueue
from shapes.rectangle import Rectangle
from shapes.triangle import Triangle
from pathlib import Path
from utils import SelfOrderingDict, get_logger, dist
from printer import Writer
import time

import os

logger = get_logger(__name__)

EPS_SPLIT = float(
    os.getenv("EPS_SPLIT", default=1e-3)
)  # epsilon for when splitting a rectangle
EPS_AREA = float(os.getenv("EPS_AREA", default=1e-2))
distance_eps = 1e-5
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

    if problem == "First problem":
        model = Bomip2C.from_file(instance_path)
    elif problem == "Second problem (BUFLP)":
        model = Bomip2buflp.from_file(instance_path)
    else:
        raise ValueError("Wrong value for the instance argument.")
    opt = pyo.SolverFactory(
        "gurobi_direct",
        executable=os.getenv(
            "SOLVER_PATH",
            default="/opt/gurobi951/linux64/bin/gurobi.sh",  # default="C:/gurobi950/win64/bin/gurobi.bat"
        ),
    )
    opt.options["MIPGap"] = os.getenv("MIPGAP", default=1e-4)
    opt.options["NumericFocus"] = 3

    tic = time.perf_counter()
    z_T = find_lexmin(model, (1, 2), opt)
    z_B = find_lexmin(model, (2, 1), opt)

    logger.debug(f"Found z_T: {z_T} and z_B: {z_B}.")

    splitting_direction = 0  # 0 horizontal, 1 vertical
    solutions_dict = SelfOrderingDict({z_T: 0, z_B: 0})
    r = Rectangle(z_T, z_B)
    pq = PriorityQueue()
    pq.put((-r.area, r, splitting_direction))

    iteration = 1
    while not pq.empty():
        logger.info(f"Iteration: {iteration}")

        _, searching_shape, splitting_direction = pq.get()

        z1 = searching_shape.topleft
        z2 = searching_shape.botright
        logger.debug(
            f"Searching shape is a {type(searching_shape)} with splitting direction {splitting_direction}"
        )
        logger.debug(f"z1: {z1}, z2: {z2}")
        if isinstance(searching_shape, Rectangle):
            logger.debug(f"Since it's a Rectangle, we apply the weighted sum method")
            z_cap = weighted_sum(model, opt=opt, rectangle=searching_shape)
            logger.debug(f"Found {len(z_cap)} z_cap values.")
            for k in range(len(z_cap) - 1):
                triangle = Triangle(z_cap[k], z_cap[k + 1])
                if triangle not in pq.queue and triangle.area > EPS_AREA:
                    logger.debug(f"Adding a triangle with area {triangle.area}")
                    pq.put((-triangle.area, triangle, splitting_direction))
                if k != 0:
                    solutions_dict[z_cap[k]] = 0
            iteration += 1

            logger.debug("Weighted sum is over, starting again.")
            continue

        logger.debug(f"Searching a Triangle now. Check if connected.")
        connected = line_detector(model, opt, searching_shape)
        if connected:
            solutions_dict[z1] = 1
            iteration += 1
            logger.debug("It's connected, starting over.")
            continue

        logger.debug("It was not connected, apply splitting.")
        if splitting_direction == 0:
            logger.debug("The splitting direction is horizontal.")
            _, t_b = searching_shape.split_horizontally()
            try:
                z1_bar = find_lexmin(model, (1, 2), opt, t_b)
                logger.debug(f"Found z1_bar: {z1_bar}")
            except ValueError:
                z1_bar = z2

            if abs(z1_bar[1] - t_b.topleft[1]) < distance_eps:
                logger.debug(f"Since z1_bar is close to {t_b.topleft}, z2_bar=z1_bar.")
                z2_bar = z1_bar
            else:
                logger.debug(
                    f"Since z1_bar is far from {t_b.topleft}, we compute z2_bar."
                )
                t_t = Triangle(z1, (z1_bar[0] - EPS_SPLIT, t_b.topleft[1]))
                try:
                    z2_bar = find_lexmin(model, (2, 1), opt, shape=t_t, verbose=False)
                    logger.debug(f"Found z2_bar: {z2_bar}")
                except ValueError:
                    z2_bar = z1
            logger.debug("Finished splitting.")
        else:
            logger.debug("Splitting direction is vertical.")
            t_t, _ = searching_shape.split_vertically()
            try:
                z2_bar = find_lexmin(model, (2, 1), opt, t_t)
                logger.debug(f"Found z2_bar: {z2_bar}")
            except ValueError:
                z2_bar = z1

            if abs(z2_bar[0] - t_t.botright[0]) < distance_eps:
                logger.debug(f"Since z2_bar is close to {t_t.botright}, z1_bar=z2_bar.")
                z1_bar = z2_bar
            else:
                logger.debug(
                    f"Since z2_bar is far from {t_t.botright}, we compute z1_bar."
                )
                t_b = Triangle((t_t.botright[0], z2_bar[1] - EPS_SPLIT), z2)

                try:
                    z1_bar = find_lexmin(model, (1, 2), opt, shape=t_b, verbose=False)
                    logger.debug(f"Found z1_bar: {z1_bar}")
                except ValueError:
                    z1_bar = z2

            logger.debug("Finished splitting.")

        new_direction = (splitting_direction + 1) % 2

        if dist(z2_bar, z1, "M") > distance_eps:
            # if z2_bar != z1:
            logger.debug("Since z2_bar is far from z1, we compute the rectangle.")
            try:
                rect = Rectangle(z1, z2_bar)
            except ValueError as e:
                iteration += 1
                logger.critical(e)
                continue

            if rect.area > EPS_AREA:
                logger.debug(f"Rectangle area is {rect.area}, adding it to the PQ.")
                pq.put((-rect.area, rect, new_direction))
                solutions_dict[z2_bar] = 0

        if dist(z1_bar, z2, "M") > distance_eps:
            # if z1_bar != z2:
            logger.debug("Since z1_bar is far from z2, we compute the rectangle.")
            try:
                rect = Rectangle(z1_bar, z2)
            except ValueError as e:
                iteration += 1
                logger.critical(e)
                continue
            if rect.area > EPS_AREA:
                logger.debug(f"Rectangle area is {rect.area}, adding it to the PQ.")
                pq.put((-rect.area, rect, new_direction))
                solutions_dict[z1_bar] = 0

        iteration += 1
        if iteration > 800:
            break

    toc = time.perf_counter() - tic

    writer = Writer("min", instance_sol_path)
    writer.print_solution(solutions_dict, tot_time=toc, iterations=iteration)
