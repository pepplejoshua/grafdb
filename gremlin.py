from graf import Graph, Graf, showProg
from model import Entity, Connection

nodes = []
names = ["marko", "vadas", "peter", "josh"]
for i in range(4):
    n = Entity(i+1, {"age": 25+i, "name": names[i]})
    nodes.append(n)

softnames = ["lop", "ripple"]
st = len(nodes)+1
for i in range(st, st+2):
    s = Entity(i, {"name": softnames[i-st], "lang": "java"})
    nodes.append(s)

conns = []

marko = nodes[0]
vardas = nodes[1]

peter = nodes[2]
josh = nodes[3]

lop = nodes[4]
ripple = nodes[5]

conns += Connection(marko, vardas, "knows", False, props={"weight": 0.5}).toEdges()
conns += Connection(marko, josh, "knows", False, props={"weight": 1.0}).toEdges()

conns += Connection(marko, lop, "created", False, props={"weight": 0.4}).toEdges()
conns += Connection(josh, lop, "created", False, props={"weight": 0.4}).toEdges()
conns += Connection(peter, lop, "created", False, props={"weight": 0.2}).toEdges()
conns += Connection(josh, ripple, "created", False, props={"weight": 1.0}).toEdges()

vert = []

for n in nodes:
    vert.append(n.toNode())

# print(conns)
# print(vert)
g = Graph(vert, conns)

q = g.v(1)._from("created").property("name", "lang")
showProg(q.program)
print("\t", q.run(), "\n", sep="")

ageGT25 = lambda v: v.get("name", "") == "josh"

q = g.v().filter(ageGT25).property("name", "age")
showProg(q.program)
print("\t", q.run(), "\n", sep="")

q = g.v(1)._from("knows")._as("k").filter(ageGT25).back("k").unique().property("name", "id", "age")
showProg(q.program)
print("\t", q.run(), "\n", sep="")