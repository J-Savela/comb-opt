import math
from pyscipopt import Model
model = Model()
x1 = model.addVar(name="x1", vtype="C", lb=-1, ub=1)
x2 = model.addVar(name="x2", vtype="C", lb=-1, ub=1)
la = model.addVar(name="la", vtype="C", lb=None, ub=None)
lb = model.addVar(name="lb", vtype="C", lb=None, ub=None)
A = {(-1, 4), (1 / 2, 4), (1 / 2, 3)}
B = {(-2, -4), (-1 / 2, -1), (-1, -4), (1 / 2, -2)}
for p in A:
    p1 = p[0]
    p2 = p[1]
    model.addCons(p1 * x1 + p2 * x2 <= la)
for p in B:
    p1 = p[0]
    p2 = p[1]
    model.addCons(p1 * x1 + p2 * x2 >= lb)
model.addCons(la <= lb)
model.setObjective(lb - la, "maximize")
model.hideOutput()
model.optimize()

x = (model.getVal(x1), model.getVal(x2))
x_len = math.sqrt(x[0]**2 + x[1]**2)
l = (model.getVal(la) + model.getVal(lb)) / 2
nvec = (l*x[0] / x_len**2, l*x[1] / x_len**2)
