"""
The Beer Distribution Problem for the PuLP Modeller

Authors: Antony Phillips, Dr Stuart Mitchell  2007
"""

# Import PuLP modeler functions
from pulp import *

# Creates a list of all the supply nodes
Warehouses = ["A", "B"]

# Creates a dictionary for the number of units of supply for each supply node
supply = {"A": 4000,
          "B": 4000}

# Creates a list of all demand nodes
Bars = ["1", "2", "3", "4", "5"]

# Creates a dictionary for the number of units of demand for each demand node
demand = {"1": 500,
          "2": 900,
          "3": 1800,
          "4": 200,
          "5": 700, }

# Creates a list of costs of each transportation path
costs1 = [  # Bars
    # 1 2 3 4 5
    [2, 4, 3, 2, 1],  # A   Warehouses
    [2, 4, 3, 2, 1]  # B
]

costs2 = [  # Bars
    # 1 2 3 4 5
    [10, 2, 30, 30, 30],  # A   Warehouses
    [0, 0, 0, 0, 0]  # B
]

# The cost data is made into a dictionary
costs1 = makeDict([Warehouses, Bars], costs1, 0)
costs2 = makeDict([Warehouses, Bars], costs2, 0)

# Creates the 'prob' variable to contain the problem data
prob = LpProblem("Beer_Distribution_Problem", LpMinimize)

# Creates a list of tuples containing all the possible routes for transport
Routes = [(w, b) for w in Warehouses for b in Bars]

# A dictionary called 'Vars' is created to contain the referenced variables(the routes)
vars = LpVariable.dicts("Route", (Warehouses, Bars), 0, None, LpInteger)

# The supply maximum constraints are added to prob for each supply node (warehouse)
for w in Warehouses:
    prob += lpSum([vars[w][b] for b in Bars]) <= supply[w], "Sum_of_Products_out_of_Warehouse_%s" % w

# The demand minimum constraints are added to prob for each demand node (bar)
for b in Bars:
    prob += lpSum([vars[w][b] for w in Warehouses]) >= demand[b], "Sum_of_Products_into_Bar%s" % b


# The objective function is added to 'prob' first
cost1 = lpSum([vars[w][b] * costs1[w][b] for (w, b) in Routes])
cost2 = lpSum([vars[w][b] * costs2[w][b] for (w, b) in Routes])

prob += cost1
# The problem is solved using PuLP's choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
for v in prob.variables():
    print(v.name, "=", v.varValue)

# The optimised objective function value is printed to the screen
print("Total Cost of Transportation = ", value(prob.objective))

# prob += cost1 <= prob.objective + 0.1
prob += cost2

# The status of the solution is printed to the screen
print("Status2:", LpStatus[prob.status])

# Each of the variables is printed with it's resolved optimum value
for v in prob.variables():
    print(v.name, "=", v.varValue)

# The optimised objective function value is printed to the screen
print("Total Cost of Transportation2 = ", value(prob.objective))
