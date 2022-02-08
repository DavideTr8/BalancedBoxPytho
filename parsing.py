from pathlib import Path

import pyomo.environ as pyo


def split_int(line: str) -> list[int]:
    """Split and transform to int each element of line."""
    return [int(x) for x in line.split()]


class Bomip2dkp:
    def __init__(
        self,
        num_binaries: int,
        rhs_1st_cstr: int,
        rhs_2nd_cstr: int,
        objective1: list[int],
        objective2: list[int],
        weights_1st_cstr: list[int],
        weights_2nd_cstr: list[int],
    ):
        """
        Class for representing a Biobjective Knapsack problem.
        :param num_binaries: int,
            number of variables.
        :param rhs_1st_cstr: int,
            right-hand side of the first constraint.
        :param rhs_2nd_cstr: int,
            right-hand side of the second constraint.
        :param objective1: list[int],
            list of all the first objective coefficients.
        :param objective2: list[int],
            list of all the second objective coefficients.
        :param weights_1st_cstr: list[int],
            list of all the first constraint coefficients.
        :param weights_2nd_cstr: list[int],
            list of all the second constraint coefficients.
        """
        self.num_binaries = num_binaries
        self.rhs_1st_cstr = rhs_1st_cstr
        self.rhs_2nd_cstr = rhs_2nd_cstr
        self.objective1 = objective1
        self.objective2 = objective2
        self.weights_1st_cstr = weights_1st_cstr
        self.weights_2nd_cstr = weights_2nd_cstr

    def to_pyomo(self) -> pyo.ConcreteModel:
        """
        Write the problem as pyomo model.
        :return: pyo.ConcreteModel
        """
        model = pyo.ConcreteModel()

        model.variables_idx = pyo.RangeSet(0, self.num_binaries - 1)

        model.x = pyo.Var(model.variables_idx, domain=pyo.Boolean)

        model.cstr1coeff = pyo.Param(
            model.variables_idx, initialize=self.weights_1st_cstr
        )
        model.rhs1 = pyo.Param(initialize=self.rhs_1st_cstr)
        model.cstr2coeff = pyo.Param(
            model.variables_idx, initialize=self.weights_2nd_cstr
        )
        model.rhs2 = pyo.Param(initialize=self.rhs_2nd_cstr)
        model.obj1coeff = pyo.Param(model.variables_idx, initialize=self.objective1)
        model.obj2coeff = pyo.Param(model.variables_idx, initialize=self.objective2)

        model.constraint1 = pyo.Constraint(
            expr=pyo.summation(model.cstr1coeff, model.x) <= model.rhs1
        )
        model.constraint2 = pyo.Constraint(
            expr=pyo.summation(model.cstr2coeff, model.x) <= model.rhs2
        )

        model.objective1 = pyo.Objective(expr=pyo.summation(model.obj1coeff, model.x))
        model.objective2 = pyo.Objective(expr=pyo.summation(model.obj2coeff, model.x))

        return model

    @classmethod
    def from_file(cls, instance_path: Path):
        """
        Parse a .txt file with instance's data.

        :param instance_path: Path,
            path for the instance.
        :return: Bomip2dpk
        """
        with open(instance_path) as tfile:
            content = tfile.readlines()

        num_binaries = int(content[0])
        rhs_1st_cstr = int(content[1])
        rhs_2nd_cstr = int(content[2])
        objective1 = split_int(content[3])
        objective2 = split_int(content[4])
        weights_1st_cstr = split_int(content[5])
        weights_2nd_cstr = split_int(content[6])

        return cls(
            num_binaries,
            rhs_1st_cstr,
            rhs_2nd_cstr,
            objective1,
            objective2,
            weights_1st_cstr,
            weights_2nd_cstr,
        )
