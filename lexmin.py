from copy import deepcopy

import pyomo.environ as pyo

from Rectangle import Rectangle


def find_lexmin(
    model: pyo.ConcreteModel,
    objective_order: tuple,
    opt: pyo.SolverFactory,
    rectangle=Rectangle(),
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
    :return: pyo.ConcreteModel
    """
    model_copy = deepcopy(model)

    model.ztop_cstr_x = pyo.Constraint(
        expr=model_copy.objective1.expr >= rectangle.topleft[0]
    )
    model.ztop_cstr_y = pyo.Constraint(
        expr=model_copy.objective2.expr <= rectangle.topleft[1]
    )
    model.zbot_cstr_x = pyo.Constraint(
        expr=model_copy.objective1.expr <= rectangle.botright[0]
    )
    model.ztop_cstr_y = pyo.Constraint(
        expr=model_copy.objective2.expr >= rectangle.botright[1]
    )

    if objective_order == (1, 2):
        model_copy.objective1.activate()
        model_copy.objective2.deactivate()

        opt.solve(model_copy)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective1.expr <= pyo.value(model_copy.objective1)
        )

        model_copy.objective1.deactivate()
        model_copy.objective2.activate()

        opt.solve(model_copy)

    elif objective_order == (2, 1):
        model_copy.objective2.activate()
        model_copy.objective1.deactivate()

        opt.solve(model_copy)

        model_copy.objective_constraint = pyo.Constraint(
            expr=model_copy.objective2.expr <= pyo.value(model_copy.objective2)
        )

        model_copy.objective2.deactivate()
        model_copy.objective1.activate()

        opt.solve(model_copy)

    else:
        raise ValueError("The objective order provided isn't accepted")

    return pyo.value(model_copy.objective1), pyo.value(model_copy.objective2)
