# Edge -> (in, out which are both scalar IDs referring to Nodes)
# Node -> (in, out which are list of IDs referring nodes both pointed to and being referred to from)
def error(msg):
    print(msg)
    return False

class Graph:
    def __init__(g, Nodes: list[any], Edges: list[any]) -> None:
        g.nodes = []
        g.edges = []
        g.nodeIndex = {}
        g.autoid = 1
        
        if isinstance(Nodes, list):
            g.addNodes(Nodes)
        if isinstance(Edges, list):
            g.addEdges(Edges)  
    
    def addNodes(g, nodes: list[any]):
        for n in nodes:
            g.addNode(n)

    def addEdges(g, edges: list[any]):
        for e in edges:
            g.addNode(e)

    def findNodeById(g, id):
        return g.nodeIndex.get(id, None)
    
    def genID(g):
        g.autoid += 1
        return g.autoid - 1

    def addNode(g, node):
        if not node.id:
            node.id = g.genID()
        elif g.findNodeById(node.id):
            return error(f"A Node with {node.id=} already exists.")

        g.nodes.append(node)    
        g.nodeIndex[node.id] = node # for quick lookups with ID
        node._in = [] # for tracking edge pointers into this vertex
        node._out = [] # for tracking edge pointers from this vertex
        return node.id

    def addEdge(g, edge):
        edge._in = g.findNodeById(edge._in)
        edge._out = g.findNodeById(edge._out)

        # if the nodes referenced in the edge don't exist, show error
        if not (edge._in and edge._out):
            sect = "out" if edge._in else "in"
            error(f"{edge=}")
            return error(f"This edge's {sect} node wasn't found")

        nodeIn = edge._in
        nodeOut = edge._out
        nodeIn._in.push(edge) # update the "in" node's in edges array
        nodeOut._out.push(edge) # update the "out" node's out edges array
