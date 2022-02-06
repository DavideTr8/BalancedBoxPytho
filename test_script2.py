import pyomo.environ as pyo

from lexmin import find_lexmin

solver_path = "/usr/local/bin/glpsol"

model = pyo.ConcreteModel()

model.x1 = pyo.Var(bounds=(-10, 10), within=pyo.Integers)
model.x2 = pyo.Var(bounds=(-10, 10), within=pyo.Integers)

model.easy_constraint = pyo.Constraint(expr=model.x1 + model.x2 <= 20)

model.objective1 = pyo.Objective(expr=1.2 * model.x1 - 5 * model.x2, sense=pyo.minimize)
model.objective2 = pyo.Objective(expr=-2 * model.x1 + 0.5 * model.x2 * 2, sense=pyo.minimize)

opt = pyo.SolverFactory('glpk', executable=solver_path)

# model.pyo.Objective1.activate()
# model.pyo.Objective2.deactivate()
#
# opt.solve(model)

model_1 = find_lexmin(model, (1, 2), opt)

print('x1 = ', round(pyo.value(model_1.x1), 2))
print('x2 = ', round(pyo.value(model_1.x2), 2))
print('pyo.objective1 = ', round(pyo.value(model_1.objective1), 2))
print('pyo.objective2 = ', round(pyo.value(model_1.objective2), 2))

model_2 = find_lexmin(model, (2, 1), opt)

print('x1 = ', round(pyo.value(model_2.x1), 2))
print('x2 = ', round(pyo.value(model_2.x2), 2))
print('pyo.objective1 = ', round(pyo.value(model_2.objective1), 2))
print('pyo.objective2 = ', round(pyo.value(model_2.objective2), 2))

# model.pyo.Objective2.deactivate()
# model.pyo.Objective1.activate()
# model.obj_constr = Constraint(expr=model.pyo.Objective2.expr >= pyo.value(model.pyo.Objective2))
# results = opt.solve(model) # solves and updates instance
# print('x1 = ',round(pyo.value(model.x1),2))
# print('x2 = ',round(pyo.value(model.x2),2))
# print('pyo.Objective1 = ',round(pyo.value(model.pyo.Objective1),2))
# print('pyo.Objective2 = ',round(pyo.value(model.pyo.Objective2),2))

# Nsteps=21
# X=[]
# Y=[]
# print('  x1  ',' x2 ',' OF1 ',' OF2 ',' Epsilon ')
# for counter in range(1,Nsteps+1):
#     model.epsilon= minOF2 + (maxOF2 - minOF2)*(counter-1)/(Nsteps-1)
#     results = opt.solve(model) # solves and updates instance
#     print("%5.2f"% pyo.value(model.x1),"%5.2f"% pyo.value(model.x2),"%5.2f"% pyo.value(model.pyo.Objective1),"%5.2f"% pyo.value(model.pyo.Objective2), "%5.2f"% pyo.value(model.epsilon))
#     X.append(pyo.value(model.pyo.Objective1))
#     Y.append(pyo.value(model.pyo.Objective2))
