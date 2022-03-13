from copy import deepcopy
import logging

import pyomo.environ as pyo

from shapes.rectangle import Rectangle
from shapes.shapee import Shape


def find_lexmin(
    model: pyo.ConcreteModel,
    objective_order: tuple,
    opt: pyo.SolverFactory,
    shape: Shape = Rectangle(),
    verbose=False,
) -> pyo.ConcreteModel:
    """
    Finds the lexmin of a biobjective minimization problem's model wrote in Pyomo where both objectives are defined as
    model.objective1 and model.objective2

    :param model: pyo.ConcreteModel
    :param objective_order: tuple,
        Order in which to solve the objectives. Can be (1, 2) or (2, 1).
    :param opt: pyo.SolverFactory,
        Solver for the model.
    :param rectangle: Rectangle,
        Rectange in which the optimization is constrained.
    :param verbose: bool (optional),
        Print the output of the solver.
    :return: pyo.ConcreteModel
    """
    model_copy = deepcopy(model)

    if objective_order == (1, 2):
        model_copy.objective1.activate()
        model_copy.objective2.deactivate()

        model_copy.ztop_cstr_y = pyo.Constraint(
            expr=model_copy.objective2.expr <= shape.topleft[1]
        )

        logging.info(
            f"Solving the first problem in lexmin with order {objective_order}"
        )
        opt.solve(model_copy, tee=verbose)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective1.expr <= pyo.value(model_copy.objective1)
        )

        model_copy.objective1.deactivate()
        model_copy.objective2.activate()
        logging.info(
            f"Solving the second problem in lexmin with order {objective_order}"
        )
        opt.solve(model_copy, tee=verbose)

    elif objective_order == (2, 1):
        model_copy.objective2.activate()
        model_copy.objective1.deactivate()

        model_copy.zbot_cstr_x = pyo.Constraint(
            expr=model_copy.objective1.expr <= shape.botright[0]
        )

        logging.info(
            f"Solving the first problem in lexmin with order {objective_order}"
        )
        opt.solve(model_copy, tee=verbose)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective2.expr <= pyo.value(model_copy.objective2)
        )

        model_copy.objective2.deactivate()
        model_copy.objective1.activate()

        logging.info(
            f"Solving the second problem in lexmin with order {objective_order}"
        )
        opt.solve(model_copy, tee=verbose)

    else:
        raise ValueError("The objective order provided isn't accepted")

    return pyo.value(model_copy.objective1), pyo.value(model_copy.objective2)


def weighted_sum(
    model: pyo.ConcreteModel, rectangle: Rectangle, opt: pyo.SolverFactory
):
    model_copy = deepcopy(model)

    z1 = rectangle.topleft
    z2 = rectangle.botright

    lambda1 = z2[0] - z2[1]
    lambda2 = z1[1] - z1[0]

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

    logging.info(f"Solving the weighted sum model.")
    opt.solve(model_copy)

    z_cap = [(pyo.value(model_copy.objective1), pyo.value(model_copy.objective2))]

    # TODO solution pool
    return z_cap


def line_detector(model, opt, triangle):
    model_copy = deepcopy(model)

    model_copy.dummy_obj = model_copy.Objective(expr=0)

    for cstr in model.component_objects(pyo.Constraint):
        cstr.activate()

    model_copy.cstr_obj_1_1 = pyo.Constraint(
        expr=model_copy.objective1.expr <= triangle.topleft[0]
    )

    model_copy.cstr_obj_2_1 = pyo.Constraint(
        expr=model_copy.objective2.expr <= triangle.topleft[1]
    )

    model_copy.cstr_obj_1_2 = pyo.Constraint(
        expr=model_copy.objective1_2.expr <= triangle.botright[0]
    )

    model_copy.cstr_obj_2_2 = pyo.Constraint(
        expr=model_copy.objective2_2.expr <= triangle.botright[1]
    )

    logging.info(f"Solving the line detector model.")
    res = opt.solve(model_copy)

    return res.Solver.Termination_condition == "optimal"
