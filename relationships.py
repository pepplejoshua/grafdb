from graf import Graph, Connection, Entity, showProg
me = Entity("joshua", {"age": 22, "skill": "coding", "specie": "human"})
henok = Entity("henok", {"age": 23, "skill": "coding", "specie": "human"})
dad = Entity("owen", {"age": 50, "skill": "dentist", "specie": "human"})
chidera = Entity("chidera", {"age": 20, "skill": "artist and programmer", "specie": "human"})
mum = Entity("miriam", {"age": 40, "skill": "business", "specie": "human"})
nala = Entity("nala", {"age": 3, "specie": "cat"})
boba = Entity("boba", {"age": 1, "specie": "dog"})
christina = Entity("christina", {"age": 22, "skill": "artist and teacher", "specie": "human"})

friendship1 = Connection(me, henok, "friend", isTwoWay=True)
friendship2 = Connection(me, chidera, "friend", isTwoWay=True)
friend3 = Connection(me, christina, "friend", isTwoWay=True)
friend4 = Connection(me, nala, "friend", isTwoWay=True)
friend5 = Connection(henok, chidera, "friend", isTwoWay=True)
dating = Connection(christina, henok, "dating", isTwoWay=True)

pet = Connection(christina, nala, "pet", isTwoWay=False)
pet2 = Connection(christina, boba, "pet", isTwoWay=False)

sonD = Connection(me, dad, "son", isTwoWay=False)
sonM = Connection(me, mum, "son", isTwoWay=False)
father = Connection(dad, me, "parent", isTwoWay=False)
mother = Connection(mum, me, "parent", isTwoWay=False)
marriage = Connection(mum, dad, "marriage", isTwoWay=True)

people = [me.toNode(), henok.toNode(), dad.toNode(), mum.toNode(), chidera.toNode()]
people += [nala.toNode(), boba.toNode(), christina.toNode()]

conns = friendship1.toEdges() + father.toEdges() + sonD.toEdges() + mother.toEdges()
conns += sonM.toEdges() + marriage.toEdges() + friendship2.toEdges()
conns += friend3.toEdges() + friend4.toEdges() + pet.toEdges()
conns += pet2.toEdges() + dating.toEdges() + friend5.toEdges()

G = Graph(people, conns)

# find all names in db
# q = G.v().property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# find my parents
# q = G.v("joshua")._from("son").property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# find my friends
# q = G.v("joshua").to("friend").property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# find my friends by knowing my mother's id
# q = G.v("miriam").to("marriage").to("son").to("friend").property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# find christina's relationships and pets
# q = G.v("christina")._from().property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# q = G.v("joshua")._as("j")._from().to().excl("j")._as("f").merge("j", "f").unique().property("id", "age", "skill")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")

# isElder = lambda p: p["age"] >= 39
# find my friends
# q = G.v("joshua").to().property("id")
# showProg(q.program)
# print("\t", q.run(), "\n", sep="")