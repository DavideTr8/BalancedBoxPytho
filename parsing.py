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


class Bomip2ap:
    pass


class Bomip2C(pyo.ConcreteModel):
    def __init__(
        self,
        m: int,
        num_binaries: int,
        num_continuous: int,
        c1: list[int],
        f1: list[int],
        c2: list[int],
        f2: list[int],
        a: dict[tuple[int, int], int],
        a_prime: list[int],
        b: list[int],
    ):
        super().__init__()
        self.m = pyo.Param(initialize=m)
        self.num_binaries = pyo.Param(initialize=num_binaries)
        self.num_continuous = pyo.Param(initialize=num_continuous)

        self.binary_idx = pyo.RangeSet(0, self.num_binaries - 1)
        self.continouos_idx = pyo.RangeSet(0, self.num_continuous - 1)
        self.nb_to_m_idx = pyo.RangeSet(self.num_binaries + 1, self.m - 2)
        self.zero_to_m_idx = pyo.RangeSet(0, self.m - 2)

        self.c1 = pyo.Param(self.continouos_idx, initialize=c1)
        self.f1 = pyo.Param(self.binary_idx, initialize=f1)
        self.c2 = pyo.Param(self.continouos_idx, initialize=c2)
        self.f2 = pyo.Param(self.binary_idx, initialize=f2)
        self.a = pyo.Param(self.continouos_idx, self.zero_to_m_idx, initialize=a)  #
        self.a_prime = pyo.Param(self.binary_idx, initialize=a_prime)
        self.b = pyo.Param(self.zero_to_m_idx, initialize=b)

        self.x = pyo.Var(self.binary_idx, domain=pyo.Boolean)
        self.y = pyo.Var(self.continouos_idx, domain=pyo.PositiveReals)

        def first_cstr_rule(model, j):
            lhs = (
                sum(
                    [
                        self.a.extract_values()[i, j] * model.y[i]
                        for i in self.continouos_idx
                    ]
                )
                + self.a_prime[j] * model.x[j]
            )
            return lhs <= self.b[j]

        self.first_cstr = pyo.Constraint(self.binary_idx, rule=first_cstr_rule)

        def second_cstr_rule(model, j):
            lhs = sum(
                [
                    self.a.extract_values()[i, j] * model.y[i]
                    for i in self.continouos_idx
                ]
            )
            return lhs <= self.b[j]

        self.second_cstr = pyo.Constraint(self.nb_to_m_idx, rule=second_cstr_rule)

        self.third_cstr = pyo.Constraint(
            expr=pyo.summation(self.x) <= self.num_binaries / 3
        )

        self.objective1 = pyo.Objective(
            expr=pyo.summation(self.c1, self.y) + pyo.summation(self.f1, self.x)
        )

        self.objective2 = pyo.Objective(
            expr=pyo.summation(self.c2, self.y) + pyo.summation(self.f2, self.x)
        )

        # Line detection part
        # line detection constraints
        self.y2 = pyo.Var(self.continouos_idx, domain=pyo.PositiveReals)

        def first_cstr_rule2(model, j):
            lhs = (
                sum(
                    [
                        self.a.extract_values()[i, j] * model.y2[i]
                        for i in self.continouos_idx
                    ]
                )
                + self.a_prime[j] * model.x[j]
            )
            return lhs <= self.b[j]

        self.first_cstr2 = pyo.Constraint(self.binary_idx, rule=first_cstr_rule2)

        def second_cstr_rule2(model, j):
            lhs = sum(
                [
                    self.a.extract_values()[i, j] * model.y2[i]
                    for i in self.continouos_idx
                ]
            )
            return lhs <= self.b[j]

        self.second_cstr2 = pyo.Constraint(self.nb_to_m_idx, rule=second_cstr_rule2)

        self.first_cstr2.deactivate()
        self.second_cstr2.deactivate()

        # line detection objectives
        self.objective1_2 = pyo.Objective(
            expr=pyo.summation(self.c1, self.y2) + pyo.summation(self.f1, self.x)
        )

        self.objective2_2 = pyo.Objective(
            expr=pyo.summation(self.c2, self.y2) + pyo.summation(self.f2, self.x)
        )

        self.objective1_2.deactivate()
        self.objective2_2.deactivate()

    @classmethod
    def from_file(cls, instance_path: Path):
        with open(instance_path) as tfile:
            content = tfile.readlines()

        m = int(content[0])
        num_continuous = int(content[1])
        num_binaries = int(content[2])

        c1 = split_int(content[3])
        f1 = split_int(content[4])
        c2 = split_int(content[5])
        f2 = split_int(content[6])

        a = {}
        for i in range(num_continuous):
            for j in range(m - 1):
                a[i, j] = split_int(content[7 + i])[j]

        checkpoint = 7 + num_continuous
        a_prime = split_int(content[checkpoint])
        b = split_int(content[checkpoint + 1])

        return cls(m, num_binaries, num_continuous, c1, f1, c2, f2, a, a_prime, b)


class Bomip2buflp:
    pass
