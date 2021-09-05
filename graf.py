from inspect import isfunction

PULL = "pull"
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
    
    def genID(g):
        g.autoid += 1
        return g.autoid - 1

    def addNode(g, node):
        if not node["id"]:
            node["id"] = g.genID()
        elif g.findNodeById(node["id"]):
            return error(f"A Node with {node['id']=} already exists.")

        g.nodes.append(node)    
        g.nodeIndex[node["id"]] = node # for quick lookups with ID
        node["_in"] = [] # for tracking edge pointers into this vertex
        node["_out"] = [] # for tracking edge pointers from this vertex
        return node["id"]

    def addEdge(g, edge):
        edge["_in"] = g.findNodeById(edge["_in"])
        edge["_out"] = g.findNodeById(edge["_out"])

        # if the nodes referenced in the edge don't exist, show error
        if not (edge["_in"] and edge["_out"]):
            sect = "out" if edge["_in"] else "in"
            error(f"{edge=}")
            return error(f"This edge's {sect} node wasn't found")

        nodeIn = edge["_in"]
        nodeOut = edge["_out"]
        nodeIn["_in"].push(edge) # update the "in" node's in edges array
        nodeOut["_out"].push(edge) # update the "out" node's out edges array

    def findVertices(g, args):
        if not len(args):
            return g.nodes[:]
        
        if isinstance(args[0], dict):
            return g.searchNodesByProperties(args[0])
        elif isinstance(args[0], str):
            return g.findNodesByIds(args)
    
    def findNodeById(g, id):
        return g.nodeIndex.get(id, None)

    def findNodesByIds(g, ids):
        if len(ids) == 1:
            node = g.findNodeById(ids[0])
            if node:
                return node
            else:
                return []
        
        mappedNodes = list(map(g.findNodeById, ids))
        nodes = list(filter(lambda n: True if n else False, mappedNodes))
        return nodes
        

    def searchNodesByProperties(g, filterProps: dict):
        fltr = lambda node: Graf["objectFilter"](node, filterProps)
        filteredNodes = list(fltr, g.nodes)
        return filteredNodes

    # create query based on current Graph and passed args
    def v(g, *args):
        q = Query(g)
        q.add("vertex", args)
        return q

class Query:
    def __init__(q, graph: Graph) -> None:
        q.graph = graph
        q.state = []
        q.program = []
        q.gremlins = []

    def add(q, pipetype, args):
        step = [pipetype, args]
        q.program.append(step)
        return q

def fauxPipetype(_, __, maybe_gremlin):
    return maybe_gremlin if maybe_gremlin else PULL

def addPipetype(name: str, fn):
    Graf["Pipetypes"][name] = fn
    qfn = lambda this, *args: this.add(name, args)
    Graf['Q'][name] = qfn

def getPipetype(name: str):
    pipetype = Graf["Pipetypes"].get(name, None) # pipetype should be a function indexed at name, or default to None

    if not pipetype:
        error(f"Unrecognized pipetype {name}")
        return fauxPipetype

    return pipetype

def filterEdges(filter):
    def filterFn(edge):
        pass
    return filterFn

def simpleTraversal(direction: str):
    def traverse(graph: Graph, args, gremlin: dict, state: dict):
        # if gremlin is None and state has no edges or edges array contains no edges, pull
        if not gremlin and (not state.get("edges", None) or not len(state["edges"])): # query init
            return PULL

        if (not state.get("edges", None) or not len(state["edges"])):
            state["gremlin"] = gremlin
            method = graph.findInEdges if direction == "in" else graph.findOutEdges # choose graph traversal method
            if not len(args):
                error("traversal pipe missing argument(s)")
                return PULL

            state["edges"] = list(filter(method(gremlin["vertex"]), Graf["filterEdges"](args[0])))

        if not len(state["edges"]): # no more edges to traverse
            return PULL

        if direction == "in":
            vertex = state["edges"].pop()._in 
        else:
            vertex = state["edges"].pop()._out
        return Graf["goToVertex"](state["gremlin"], vertex)
    return traverse

Graf = {}
Graf["Graph"] = Graph
Graf["G"] = {}
Graf["Query"] = Query
Graf["Q"] = {}
Graf["error"] = error
Graf["Pipetypes"] = {}
Graf["addPipetype"] = addPipetype
Graf["getPipetype"] = getPipetype
Graf["simpleTraversal"] = simpleTraversal
Graf["filterEdges"] = filterEdges

def addVertexPipetype(graph: Graph, args, gremlin: dict , state: dict):
    if not state.get("vertices", False):
        state["vertices"] = graph.findVertices(args) # init state. what is this state for? it contains matching vertices if any from graph
        # findVertices routes the search of the graph based on dictionaries or ids
    if len(state["vertices"]) < 1:
        return "done"

    vertex = state["vertices"].pop() # pop the last vertex

    # return a gremlin sitting on this vertex sharing state with any passed gremlins
    if gremlin:
        return Graf["makeGremlin"](vertex, gremlin.get("state", {}))
    else:
        return Graf["makeGremlin"](vertex, {})

def addPropertyPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    if not len(args):
        error("property pipe missing argument(s)")
        return PULL

    gremlin["result"] = gremlin["vertex"].get(args[0], None)
    return False if not gremlin["result"] else gremlin # return false if we can't find matching props on Nodes

def addUniquePipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    if state.get(gremlin["vertex"]["id"], False):
        return PULL
    
    state[gremlin["vertex"]["id"]] = True
    return gremlin

def addFilterPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    if not len(args):
        error("filter pipe missing argument(s)")
        return PULL

    if isinstance(args[0], dict):
        return Graf["objectFilter"](gremlin["vertex"], args[0])
    elif callable(args[0]) or isfunction(args[0]):
        fn = args[0]
        if not fn(gremlin["vertex"], gremlin): # if the gremlin fails filter function, pull
            return PULL
        return gremlin
    else:
        error(f"Filter is not a function or object filter: {args[0]}")
        return gremlin

def addTakePipetype(graph: Graph, args, gremlin: dict, state: dict):
    state["taken"] = state["taken"] if state.get("taken", False) else 0
    
    if not len(args):
        error("take pipe missing argument(s)")
        return PULL

    if state["taken"] == args[0]:
        state["taken"] = 0 # this allows us to reuse the query later
        return "done" # closes all previous pipes

    if not gremlin:
        return PULL

    state["taken"] += 1
    return gremlin

def addAsPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    gremlin["state"]["as"] = gremlin["state"]["as"] if gremlin["state"].get("as", False) else {}
    gremlin["state"]["as"][args[0]] = gremlin["vertex"]
    return gremlin

def addMergePipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not state.get("vertices", False) and not gremlin:
        return PULL

    if not state.get("vertices", False) and not len(state["vertices"]):
        gr_state = gremlin["state"] if gremlin.get("state", False) else {}
        obj = gr_state["as"] if gr_state.get("as", False) else {}

        # check if each argument (as rename) exists in obj dict
        mappedArguements = list(map(lambda id: obj.get(id, False), args)) 
        # filter the vertices we can find that match
        state["vertices"] = list(filter(lambda id: True if id else False, mappedArguements))

    if not len(state["vertices"]):
        return PULL

    vertex = state["vertices"].pop()
    return Graf["makeGremlin"](vertex, gremlin["state"])

def addExceptPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    if not len(args):
        error("take pipe missing argument(s)")
        return PULL

    if gremlin["vertex"] == gremlin["state"]["as"][args[0]]:
        return PULL
    return gremlin

def addBackPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL
    return Graf["goToVertex"](gremlin, gremlin["state"]["as"][args[0]])

def makeGremlin(vertex: dict, state: dict) -> dict:
    newState = state if state else {}
    return {vertex: vertex, state: newState}

def goToVertex(gremlin: dict, vertex: dict) -> dict: # clones a gremlin to a vertex location
    return makeGremlin(vertex, gremlin["state"])

Graf["addPipetype"]("vertex", addVertexPipetype)
Graf["addPipetype"]("in", Graf["simpleTraversal"]("in"))
Graf["addPipetype"]("out", Graf["simpleTraversal"]("out"))
Graf["addPipetype"]("property", addPropertyPipetype)
Graf["addPipetype"]("unique", addUniquePipetype)
Graf["addPipetype"]("filter", addFilterPipetype)
Graf["addPipetype"]("take", addTakePipetype)
Graf["addPipetype"]("as", addAsPipetype)
Graf["addPipetype"]("merge", addMergePipetype)
Graf["addPipetype"]("except", addExceptPipetype)
Graf["makeGremlin"] = makeGremlin
Graf["goToVertex"] = goToVertex
