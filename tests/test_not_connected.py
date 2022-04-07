import pyomo.environ as pyo
from lexmin import weighted_sum, find_lexmin, line_detector

from shapes.rectangle import Rectangle
from shapes.triangle import Triangle

model = pyo.ConcreteModel()

model.x = pyo.Var(within=pyo.NonNegativeIntegers)
model.y = pyo.Var(within=pyo.PositiveReals)
model.y2 = pyo.Var(within=pyo.PositiveReals)

model.cstr1 = pyo.Constraint(expr=model.x + 1.0001 * model.y >= 2.0001)


model.cstr1_2 = pyo.Constraint(expr=model.x + 1.0001 * model.y2 >= 2.0001)


model.objective1 = pyo.Objective(expr=model.x)
model.objective2 = pyo.Objective(expr=model.y)
model.objective1_2 = pyo.Objective(expr=model.x)
model.objective2_2 = pyo.Objective(expr=model.y2)

model.cstr1_2.deactivate()
model.objective1_2.deactivate()
model.objective2_2.deactivate()

opt = pyo.SolverFactory(
    "gurobi_direct",
    executable="/opt/gurobi951/linux64/bin/gurobi.sh",  # default="C:/gurobi950/win64/bin/gurobi.bat"
)


z_T = find_lexmin(model, (1, 2), opt)
z_B = find_lexmin(model, (2, 1), opt)

rectangle = Rectangle(z_T, z_B)
z_cap = weighted_sum(model, opt=opt, rectangle=rectangle)

connected = line_detector(model, opt, Triangle((1, 1), (2, 0.0001)))
