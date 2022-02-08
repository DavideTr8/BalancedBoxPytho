from parsing import Bomip2dkp, Path, pyo

dataset_path = Path("./BOMIP/Part I- Integer Programs/instances/")
problem = "2DKP"
problem_class = "class A"
instance = "1dat.txt"

instance_path = dataset_path / problem / problem_class / instance
problem = Bomip2dkp.from_file(instance_path)

solver_path = "/usr/local/bin/glpsol"
opt = pyo.SolverFactory("glpk", executable=solver_path)

model = problem.to_pyomo()
model.objective1.activate()
model.objective2.deactivate()
opt.solve(model)

z_T = (pyo.value(model.objective1), pyo.value(model.objective2))

model.objective2.activate()
model.objective1.deactivate()
opt.solve(model)

z_B = (pyo.value(model.objective1), pyo.value(model.objective2))
