from copy import deepcopy

import pyomo.environ as pyo


def find_lexmin(
    model: pyo.ConcreteModel, objective_order: tuple, opt: pyo.SolverFactory
) -> pyo.ConcreteModel:
    """
    Finds the lexmin of a biobjective minimization problem's model wrote in Pyomo where both objectives are defined as
    model.objective1 and model.objective2

    :param model: pyo.ConcreteModel
    :param objective_order: tuple,
        Order in which to solve the objectives. Can be (1, 2) or (2, 1).
    :param opt: pyo.SolverFactory,
        Solver for the model.
    :return: pyo.ConcreteModel
    """
    model_copy = deepcopy(model)
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

    return model_copy
