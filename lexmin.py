import logging
from os import getenv
from copy import deepcopy

import pyomo.environ as pyo

from shapes.rectangle import Rectangle
from shapes.shapee import Shape
from shapes.Point import Point
from utils import get_logger

logger = get_logger(__name__)


def find_lexmin(
    model: pyo.ConcreteModel,
    objective_order: tuple,
    opt: pyo.SolverFactory,
    shape: Shape = Rectangle(),
    verbose=False,
) -> Point:
    """
    Finds the lexmin of a biobjective minimization problem's model wrote in Pyomo where both objectives are defined as
    model.objective1 and model.objective2

    :param model: pyo.ConcreteModel
    :param objective_order: tuple,
        Order in which to solve the objectives. Can be (1, 2) or (2, 1).
    :param opt: pyo.SolverFactory,
        Solver for the model.
    :param shape: Shape,
        Rectange in which the optimization is constrained.
    :param verbose: bool (optional),
        Print the output of the solver.
    :return: Point
    """
    model_copy = deepcopy(model)
    model_copy.name = "Lexmin"

    if objective_order == (1, 2):
        model_copy.objective1.activate()
        model_copy.objective2.deactivate()

        model_copy.ztop_cstr_y = pyo.Constraint(
            expr=model_copy.objective2.expr <= shape.topleft[1]
        )

        # if isinstance(shape, Rectangle):
        model_copy.zbot_cstr_x = pyo.Constraint(
            expr=model_copy.objective1.expr <= shape.botright[0]
        )

        model_copy.ztop_cstr_x = pyo.Constraint(
            expr=model_copy.objective1.expr >= shape.topleft[0]
        )

        logger.info(f"Solving the first problem in lexmin with order {objective_order}")
        opt.solve(model_copy, tee=verbose)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective1.expr <= pyo.value(model_copy.objective1)
        )
        logger.debug(f"Additional constraint z1 <= {pyo.value(model_copy.objective1)}")

        model_copy.objective1.deactivate()
        model_copy.objective2.activate()
        logger.info(
            f"Solving the second problem in lexmin with order {objective_order}"
        )
        res = opt.solve(model_copy, tee=verbose)

    elif objective_order == (2, 1):
        model_copy.objective2.activate()
        model_copy.objective1.deactivate()

        # if isinstance(shape, Rectangle):
        model_copy.ztop_cstr_y = pyo.Constraint(
            expr=model_copy.objective2.expr <= shape.topleft[1]
        )
        model_copy.zbot_cstr_x = pyo.Constraint(
            expr=model_copy.objective1.expr <= shape.botright[0]
        )

        model_copy.zbot_cstr_y = pyo.Constraint(
            expr=model_copy.objective2.expr >= shape.botright[1]
        )

        logger.info(f"Solving the first problem in lexmin with order {objective_order}")
        opt.solve(model_copy, tee=verbose)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective2.expr <= pyo.value(model_copy.objective2)
        )
        logger.debug(f"Additional constraint z2 <= {pyo.value(model_copy.objective2)}")

        model_copy.objective2.deactivate()
        model_copy.objective1.activate()

        logger.info(
            f"Solving the second problem in lexmin with order {objective_order}"
        )
        res = opt.solve(model_copy, tee=verbose)

    else:
        raise ValueError("The objective order provided isn't accepted")

    if res.Solver.Termination_condition != "optimal":
        raise ValueError("Solution not found.")

    return Point((pyo.value(model_copy.objective1), pyo.value(model_copy.objective2)))


def weighted_sum(
    model: pyo.ConcreteModel,
    rectangle: Rectangle,
    opt: pyo.SolverFactory,
    z_cap=None,
):
    EPS_WS = float(getenv("EPS_WS", default=1e-4))
    model_copy = deepcopy(model)
    model_copy.name = "WeightedSum"

    z1 = rectangle.topleft
    z2 = rectangle.botright

    lambda1 = z1[1] - z2[1]
    lambda2 = z2[0] - z1[0]

    model_copy.weighted_obj = pyo.Objective(
        expr=model_copy.objective1.expr * lambda1 + model_copy.objective2.expr * lambda2
    )

    model_copy.objective1.deactivate()
    model_copy.objective2.deactivate()
    model_copy.weighted_obj.activate()

    model_copy.ztop_cstr_y = pyo.Constraint(
        expr=model_copy.objective2.expr <= rectangle.topleft[1]
    )

    model_copy.zbot_cstr_x = pyo.Constraint(
        expr=model_copy.objective1.expr <= rectangle.botright[0]
    )

    model_copy.ztop_cstr_y2 = pyo.Constraint(
        expr=model_copy.objective2.expr >= rectangle.botright[1]
    )

    model_copy.zbot_cstr_x2 = pyo.Constraint(
        expr=model_copy.objective1.expr >= rectangle.topleft[0]
    )

    logger.info(f"Solving the weighted sum model.")
    opt.solve(model_copy)

    if z_cap is None:
        z_cap = [z1, z2]
    if model_copy.solutions.solutions:
        try:
            z_star = Point(
                (pyo.value(model_copy.objective1), pyo.value(model_copy.objective2))
            )
            if z_star not in z_cap:
                z_cap.append(z_star)
            if (
                pyo.value(model_copy.weighted_obj)
                < lambda1 * z1[0] + lambda2 * z1[1] - EPS_WS
            ):
                logger.debug(
                    f"{pyo.value(model_copy.weighted_obj)} < {lambda1 * z1[0] + lambda2 * z1[1]}"
                )
                logger.debug(
                    f"{pyo.value(model_copy.weighted_obj)} < {lambda1 * z2[0] + lambda2 * z2[1]}"
                )

                r1 = Rectangle(z1, z_star)
                r2 = Rectangle(z_star, z2)
                z_cap = weighted_sum(model, r1, opt, z_cap=z_cap)
                z_cap = weighted_sum(model, r2, opt, z_cap=z_cap)
        except ValueError:
            logging.warning("Solution not found in weighted sum method.")

    z_cap.sort(key=lambda x: x[0])
    return z_cap


def line_detector(model, opt, triangle):
    model_copy = deepcopy(model)
    model_copy.name = "LineDetector"
    model_copy.gamma = pyo.Var(domain=pyo.NonNegativeReals)
    model_copy.dummy_obj = pyo.Objective(expr=model_copy.gamma)

    for cstr in model_copy.component_objects(pyo.Constraint):
        cstr.activate()

    model_copy.cstr_obj_1_1 = pyo.Constraint(
        expr=model_copy.objective1.expr <= triangle.topleft[0] + model_copy.gamma
    )

    model_copy.cstr_obj_2_1 = pyo.Constraint(
        expr=model_copy.objective2.expr <= triangle.topleft[1] + model_copy.gamma
    )

    model_copy.cstr_obj_1_2 = pyo.Constraint(
        expr=model_copy.objective1_2.expr <= triangle.botright[0] + model_copy.gamma
    )

    model_copy.cstr_obj_2_2 = pyo.Constraint(
        expr=model_copy.objective2_2.expr <= triangle.botright[1] + model_copy.gamma
    )

    model_copy.objective1.deactivate()
    model_copy.objective2.deactivate()
    model_copy.dummy_obj.activate()

    logger.info(f"Solving the line detector model.")
    res = opt.solve(model_copy)

    connected = (
        res.Solver.Termination_condition == "optimal"
        and pyo.value(model_copy.gamma) <= 1e-6
    )
    logger.debug(
        f"Solver status: {res.Solver.Termination_condition}\n" f"Connected? {connected}"
    )

    return connected
