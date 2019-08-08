import assignment3
import sys

presolving = True
if len(sys.argv) >= 4 and sys.argv[3] == "--no-presolving":
    presolving = False
model = sys.argv[1]
filename = sys.argv[2]
graphname = filename.split('/')[len(filename.split('/')) - 1]

print(f"graph: {graphname}")
print(f"model: {model}")
print(f"presolving: {presolving}")
vertices, maxDeg, edgelist = assignment3.read_dimacs(filename)

if model == "AS":
    print(assignment3.coloring_AS(vertices, maxDeg, edgelist, presolving))
elif model == "ASSB":
    print(assignment3.coloring_ASSB(vertices, maxDeg, edgelist, presolving))
elif model == "PO":
    print(assignment3.coloring_PO(vertices, maxDeg, edgelist, presolving))
elif model == "POST":
    print(assignment3.coloring_POST(vertices, maxDeg, edgelist, presolving))
