# IP-models for graph coloring.
# Input as an edge list.
# Output the number of colors.
from pyscipopt import Model


# Reads dimacs graph
# Returns: vertex set, max degree, edge list
def read_dimacs(filename):
    with open(filename, "r") as fin:
        # Find header
        while True:
            row = fin.readline()
            if len(row) > 0 and row[0] == 'p':
                header = row[:(len(row)-1)]
                break
        vCount = header.split(' ')[2]
        vertices = set(range(1, vCount + 1))
        degrees = dict(map(lambda x: (x, 0), vertices))
        edgelist = []
        while True:
            row = fin.readline()
            if row == '':
                break
            if row[0] != 'e':
                continue
            row = row[:(len(row)-1)]
            splitted =row.split(' ')
            v1 = int(splitted[1])
            v2 = int(splitted[2])
            degrees[v1] += 1
            degrees[v2] += 1
            edgelist.append((v1, v2))
        maxDegree = max(degrees.values())
        return vertices, maxDegree, edgelist


# Standard assignment based model (Equations 1-4)
def coloring_AS(vertices, maxDeg, edgelist):
    max_color = maxDeg + 1
    colors = set(range(1, max_color + 1))

    # Create model and add variables
    model = Model()
    var_x = dict(map(lambda x: (x, None), {(v, i) for v in vertices for i in colors}))
    var_w = dict(map(lambda x: (x, None), colors))
    for k in var_x.keys():
        var_x[k] = model.addVar(name=f"x{k}", vtype="I", lb=0, ub=1)
    for k in var_w.keys():
        var_w[k] = model.addVar(name=f"w({k})", vtype="I", lb=0, ub=1)

    var_x_by_vertex = dict(map(lambda x: (x, set()), vertices))
    var_x_by_color = dict(map(lambda x: (x, set()), colors))
    for k, v in var_x.items():
        var_x_by_vertex[k[0]].add(v)
        var_x_by_color[k[1]].add(v)

    # Set objective
    # Equation 1
    model.setObjective(sum(var_w.values()), "minimize")

    # Add constraints
    # Equation 2
    for v in vertices:
        model.addCons(sum(var_x_by_vertex[v]) == 1, name=f"eq2_{v}")

    # Equation 3
    for e in edgelist:
        for i in colors:
            u = e[0]
            v = e[1]
            model.addCons(var_x[(u, i)] + var_x[(v, i)] <= var_w[i], name=f"eq3_{e}_{i}")

    model.hideOutput()
    model.optimize()
    return f"result: {model.getStatus()}\nobjective: {model.getObjVal()}"


# Standard assignment based model with symmetry breaking (Equations 1-6)
def coloring_ASSB(vertices, maxDeg, edgelist):
    max_color = maxDeg + 1
    colors = set(range(1, max_color + 1))

    # Create model and add variables
    model = Model()
    var_x = dict(map(lambda x: (x, None), {(v, i) for v in vertices for i in colors}))
    var_w = dict(map(lambda x: (x, None), colors))
    for k in var_x.keys():
        var_x[k] = model.addVar(name=f"x{k}", vtype="I", lb=0, ub=1)
    for k in var_w.keys():
        var_w[k] = model.addVar(name=f"w({k})", vtype="I", lb=0, ub=1)

    var_x_by_vertex = dict(map(lambda x: (x, set()), vertices))
    var_x_by_color = dict(map(lambda x: (x, set()), colors))
    for k, v in var_x.items():
        var_x_by_vertex[k[0]].add(v)
        var_x_by_color[k[1]].add(v)

    # Set objective
    # Equation 1
    model.setObjective(sum(var_w.values()), "minimize")

    # Add constraints
    # Equation 2
    for v in vertices:
        model.addCons(sum(var_x_by_vertex[v]) == 1, name=f"eq2_{v}")

    # Equation 3
    for e in edgelist:
        for i in colors:
            u = e[0]
            v = e[1]
            model.addCons(var_x[(u, i)] + var_x[(v, i)] <= var_w[i], name=f"eq3_{e}_{i}")

    # Equation 5
    for i in colors:
        model.addCons(var_w[i] <= sum(var_x_by_color[i]), name=f"eq5_{i}")

    # Equation 6
    for i in colors.difference({1}):
        model.addCons(var_w[i] <= var_w[i-1], name=f"eq6_{i}")

    model.hideOutput()
    model.optimize()
    return f"result: {model.getStatus()}\nobjective: {model.getObjVal()}"


# Partial order based model (Equations 7-14)
def coloring_PO(vertices, maxDeg, edgelist):
    max_color = maxDeg + 1
    colors = set(range(1, max_color + 1))

    # Create model and add variables
    model = Model()
    pairs = {(v, i) for v in vertices for i in colors}
    var_g = dict(map(lambda x: (x, None), pairs))
    var_l = dict(map(lambda x: (x, None), pairs))
    for k in pairs:
        var_g[k] = model.addVar(name=f"g{k}", vtype="I", lb=0, ub=1)
        var_l[k] = model.addVar(name=f"l{k}", vtype="I", lb=0, ub=1)

    # Set objective
    # Equation 7
    vertex_w = 1
    variables = set(map(lambda i: var_g[(vertex_w, i)], colors))
    model.setObjective(1 + sum(variables), "minimize")

    # Add constraints
    # Equations 8-9
    for v in vertices:
        model.addCons(var_l[(v, 1)] == 0, name=f"eq8_{v}")
        model.addCons(var_g[(v, max_color)] == 0, name=f"eq9_{v}")

    # Equations 10-11, 13
    for v in vertices:
        for i in colors.difference({max_color}):
            model.addCons(var_g[(v, i)] - var_g[(v, i + 1)] >= 0, name=f"eq10_{v}_{i}")
            model.addCons(var_g[(v, i)] + var_l[(v, i + 1)] == 1, name=f"eq11_{v}_{i}")
            model.addCons(var_g[(vertex_w, i)] - var_g[(v, i)] >= 0, name=f"eq13_{v}_{i}")

    # Equation 12
    for e in edgelist:
        for i in colors:
            u = e[0]
            v = e[1]
            model.addCons(var_g[(u, i)] + var_l[(u, i)] + var_g[(v, i)] + var_l[(v, i)] >= 1, name=f"eq12_{e}_{i}")

    model.hideOutput()
    model.optimize()
    return f"result: {model.getStatus()}\nobjective: {model.getObjVal()}"


# Partial order based model (Equations 7-11, 13-16)
def coloring_POST(vertices, maxDeg, edgelist):
    max_color = maxDeg + 1
    colors = set(range(1, max_color + 1))

    # Create model and add variables
    model = Model()
    pairs = {(v, i) for v in vertices for i in colors}
    var_x = dict(map(lambda x: (x, None), pairs))
    var_g = dict(map(lambda x: (x, None), pairs))
    var_l = dict(map(lambda x: (x, None), pairs))
    for k in pairs:
        var_x[k] = model.addVar(name=f"g{k}", vtype="I", lb=0, ub=1)
        var_g[k] = model.addVar(name=f"g{k}", vtype="I", lb=0, ub=1)
        var_l[k] = model.addVar(name=f"l{k}", vtype="I", lb=0, ub=1)

    # Set objective
    # Equation 7
    vertex_w = 1
    variables = set(map(lambda i: var_g[(vertex_w, i)], colors))
    model.setObjective(1 + sum(variables), "minimize")

    # Add constraints
    # Equations 8-9
    for v in vertices:
        model.addCons(var_l[(v, 1)] == 0, name=f"eq8_{v}")
        model.addCons(var_g[(v, max_color)] == 0, name=f"eq9_{v}")

    # Equations 10-11, 13
    for v in vertices:
        for i in colors.difference({max_color}):
            model.addCons(var_g[(v, i)] - var_g[(v, i + 1)] >= 0, name=f"eq10_{v}_{i}")
            model.addCons(var_g[(v, i)] + var_l[(v, i + 1)] == 1, name=f"eq11_{v}_{i}")
            model.addCons(var_g[(vertex_w, i)] - var_g[(v, i)] >= 0, name=f"eq13_{v}_{i}")

    # Equation 15-16
    for i in colors:
        for v in vertices:
            model.addCons(var_x[(v, i)] == 1 - (var_g[(v, i)] + var_l[(v, i)]), name=f"eq15_{v}_{i}")
        for e in edgelist:
            u = e[0]
            v = e[1]
            model.addCons(var_x[(u, i)] + var_x[(v, i)] <= 1, name=f"eq16_{e}_{i}")

    model.hideOutput()
    model.optimize()
    return f"result: {model.getStatus()}\nobjective: {model.getObjVal()}"


