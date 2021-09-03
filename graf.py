
#     def grandparentsOf(g, nodes):
#         return g.parentsOf(g.parentsOf(nodes))

#     def parentsOf(g, nodes):
#         acc = []
#         # we loop over all edges
#         for parent, child in g.edges:
#             if child in nodes:
#                 # and accumulate when we find a child we are interested in, we track its parent
#                 acc.append(parent)
#         return acc

#     def childrenOf(g, nodes):
#         acc = []
#         # we loop over all edges
#         for parent, child in g.edges:
#             if parent in nodes:
#                 # and accumulate when we find a parent we are interested in, we track its child
#                 acc.append(child)
#         return acc

#     def areSiblings(g, X, Y):
#         parentsX = g.parentsOf([X])

#         for p in parentsX:
#             if Y in g.childrenOf([p]):
#                 return True
#         return False
    
#     def print(g, res, prompt: str =""):
#         print(f"{prompt} => {res}")

# Nodes = ["tamunoiwarilama the 1st", "owen", "joshua", "miriam"]
# Edges = [
#     ["tamunoiwarilama the 1st", "owen"], ["owen", "joshua"], ["miriam", "joshua"],
#     ["miriam", "ella"], ["owen", "ella"], ["owen", "sandra"], ["miriam", "sandra"],
#     ["sandra", "greatness"], ["joshua", "henok"], ["joshua", "bryan"],
# ]

# g = Graph(Nodes, Edges)

# # print(f"{g.edges=}")
# g.print(g.parentsOf(["joshua"]), "The parents of joshua are ")
# g.print(g.grandparentsOf(["joshua"]), "A grandparent of joshua is ")
# g.print(g.areSiblings("ella", "joshua"), "joshua and ella are siblings? ")
# g.print(g.areSiblings("henok", "joshua"), "joshua and henok are siblings? ")
# g.print(g.childrenOf(["sandra"]), "sandra's children are ")
# g.print(g.childrenOf(["joshua"]), "joshua's children include but are not restricted to: ")