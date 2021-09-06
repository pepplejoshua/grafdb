from inspect import isfunction
from model import Connection, Entity
from rich import print
import json
from functools import reduce

PULL = "pull"
def error(msg):
    print(msg)
    return False

class Graph:
    def __init__(g, Nodes: list[dict], Edges: list[dict]) -> None:
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
            g.addEdge(e)
    
    def genID(g):
        g.autoid += 1
        return g.autoid - 1

    def addNode(g, node):
        if not node.get("id", False):
            node["id"] = g.genID()
        elif g.findNodeById(node["id"]):
            return error(f"A Node with {node['id']=} already exists.")

        g.nodes.append(node)    
        g.nodeIndex[node["id"]] = node # for quick lookups with ID
        node["from"] = [] # for tracking edge pointers from this vertex
        node["to"] = [] # for tracking edge pointers into this vertex
        return node["id"]

    def addEdge(g, edge):
        edge["from"] = g.findNodeById(edge["from"])
        edge["to"] = g.findNodeById(edge["to"])

        # if the nodes referenced in the edge don't exist, show error
        if not (edge["from"] and edge["to"]):
            sect = "to" if edge["from"] else "from"
            error(f"{edge=}")
            return error(f"This edge's {sect} node wasn't found")

        nodeFrom = edge["from"]
        nodeTo = edge["to"]
        nodeFrom["from"].append(edge) # update the "from" node's in edges array
        nodeTo["to"].append(edge) # update the "to" node's out edges array

    def findVertices(g, args):
        if not len(args):
            return g.nodes[:]
        
        if isinstance(args[0], dict):
            return g.searchNodesByProperties(args[0])
        else:
            return g.findNodesByIds(args)
    
    def findNodeById(g, id):
        return g.nodeIndex.get(id, None)

    def findNodesByIds(g, ids):
        if len(ids) == 1:
            node = g.findNodeById(ids[0])
            if node:
                return [node]
            else:
                return []
        
        mappedNodes = list(map(g.findNodeById, ids))
        nodes = list(filter(lambda n: True if n else False, mappedNodes))
        return nodes
        

    def searchNodesByProperties(g, filterProps: dict):
        fltr = lambda node: Graf["objectFilter"](node, filterProps)
        filteredNodes = list(fltr, g.nodes)
        return filteredNodes

    def findFromEdges(g, node):
        return node["from"]

    def findToEdges(g, node):
        return node["to"]

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

    def to(q, *args):
        q.add("to", args)
        return q

    def _from(q, *args):
        q.add("from", args)
        return q

    def unique(q, *args):
        q.add("unique", args)
        return q

    def property(q, *args):
        q.add("property", args)
        return q

    def filter(q, *args):
        q.add("filter", args)
        return q

    def take(q, *args):
        q.add("take", args)
        return q

    def _as(q, *args):
        q.add("as", args)
        return q

    def merge(q, *args):
        q.add("merge", args)
        return q
    
    def excl(q, *args):
        q.add("except", args)
        return q

    def back(q, *args):
        q.add("back", args)
        return q

    def run(q):
        q.program = Graf["transform"](q.program) # transform program before running
        MAX = len(q.program) - 1 # last step in program
        maybe_gremlin = False # gremlin dict, signal string or False
        q_results = [] # results for particular q run
        done_s = -1 # tracking linearly what steps have finished
        prog_c = MAX # program counter
        q.state = [None] * (prog_c + 1)

        
        while done_s < MAX:
            query_s = q.state
            c_step = q.program[prog_c]
            query_s[prog_c] = query_s[prog_c] if query_s[prog_c] else {}
            state = query_s[prog_c] # previous line makes sure state is a dict
            pipetypeFn = Graf["getPipetype"](c_step[0])
            maybe_gremlin = pipetypeFn(q.graph, c_step[1], maybe_gremlin, state)
            if maybe_gremlin == PULL:
                maybe_gremlin = False
                if prog_c-1 > done_s:
                    prog_c -= 1 # go to previous pipe
                    continue
                else:
                    done_s = prog_c

            if maybe_gremlin == "done":
                maybe_gremlin = False
                done_s = prog_c
            prog_c += 1

            if prog_c > MAX:
                if maybe_gremlin:
                    q_results.append(maybe_gremlin)
                maybe_gremlin = False
                prog_c -= 1

        getGremlinResult = lambda grem: grem["result"] if grem.get("result", False) else grem["vertex"]
        q_results = list(map(getGremlinResult, q_results))
        q_results.reverse()
        return q_results


def fauxPipetype(_, __, maybe_gremlin):
    return maybe_gremlin if maybe_gremlin else PULL

def addPipetype(name: str, fn):
    Graf["Pipetypes"][name] = fn
    qfn = lambda this, *args: this.add(name, args)
    Graf[name] = qfn

def getPipetype(name: str):
    pipetype = Graf["Pipetypes"].get(name, None) # pipetype should be a function indexed at name, or default to None

    if not pipetype:
        error(f"Unrecognized pipetype {name}")
        return fauxPipetype

    return pipetype

def filterEdges(filter):
    def filterFn(edge):
        if not filter:
            return True # match all
        if isinstance(filter, str):
            return edge["label"] == filter
        if isinstance(filter, list):
            return edge["label"] in filter
        return Graf["objectFilter"](edge, filter)
    return filterFn

def objectFilter(obj: dict, filterProps: dict) -> bool:
    for key in filterProps.keys():
        if obj.get(key, False):
            if obj[key] != filterProps[key]:
                return False
        else:
            return False
    return True

def makeGremlin(vertex: dict, state: dict) -> dict:
    newState = state if state else {}
    return {"vertex": vertex, "state": newState}

def goToVertex(gremlin: dict, vertex: dict) -> dict: # clones a gremlin to a vertex location
    return makeGremlin(vertex, gremlin["state"])

def simpleTraversal(direction: str):
    def traverse(graph: Graph, args, gremlin: dict, state: dict):
        # if gremlin is None and state has no edges or edges array contains no edges, pull
        if not gremlin and (not state.get("edges", None) or not len(state["edges"])): # query init
            return PULL

        # routes directly to edge containing the vertices
        if (not state.get("edges", None) or not len(state["edges"])):
            state["gremlin"] = gremlin
            method = graph.findFromEdges if direction == "from" else graph.findToEdges # choose graph traversal method
            if not len(args):
                state["edges"] = list(filter(Graf["filterEdges"](None), method(gremlin["vertex"])))
            else:
                state["edges"] = list(filter(Graf["filterEdges"](args[0]), method(gremlin["vertex"])))

        if not len(state["edges"]): # no more edges to traverse
            return PULL

        # handles routing to the vertex in the edge 
        if direction == "from":
            vertex = state["edges"].pop()["to"]
        else:
            vertex = state["edges"].pop()["from"]
        return Graf["goToVertex"](state["gremlin"], vertex)
    return traverse

Graf = {}
Graf["Graph"] = Graph
Graf["Query"] = Query
Graf["error"] = error
Graf["Pipetypes"] = {}
Graf["addPipetype"] = addPipetype
Graf["getPipetype"] = getPipetype
Graf["simpleTraversal"] = simpleTraversal
Graf["makeGremlin"] = makeGremlin
Graf["goToVertex"] = goToVertex
Graf["filterEdges"] = filterEdges
Graf["objectFilter"] = objectFilter

def addVertexPipetype(graph: Graph, args, gremlin: dict , state: dict):
    if state.get("vertices", False) == False:
        state["vertices"] = graph.findVertices(args) # init state. what is this state for? it contains matching vertices if any from graph
        # findVertices routes the search of the graph based on dictionaries or ids
    if len(state["vertices"]) < 1:
        return "done"

    # print(state["vertices"])
    vertex = state["vertices"].pop() # pop the last vertex

    # return a gremlin sitting on this vertex sharing state with any passed gremlins
    if gremlin:
        return Graf["makeGremlin"](vertex, gremlin.get("state", {}))
    else:
        return Graf["makeGremlin"](vertex, {})

def addPropertyPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin or not isinstance(gremlin, dict):
        return PULL

    if not len(args):
        error("property pipe missing argument(s)")
        return PULL

    props = {}
    for key in args:
        val = gremlin["vertex"].get(key, False)
        if not val:
            continue
        props[key] = val
    
    if len(props.keys()) == 1:
        pks = list(props.keys())
        k = pks[0]
        gremlin["result"] = props[k]
    else:
        gremlin["result"] = props
    # gremlin["result"] = gremlin["vertex"].get(args[0], None)
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
        res = Graf["objectFilter"](gremlin["vertex"], args[0])
        if res:
            return gremlin
        else:
            return PULL
    elif callable(args[0]) or isfunction(args[0]):
        fn = args[0]
        if not fn(gremlin["vertex"]): # if the gremlin fails filter function, pull
            return PULL
        return gremlin
    else:
        error(f"Filter is not a function or object filter: {args[0]}")
        return gremlin

# fix this
def addTakePipetype(graph: Graph, args, gremlin: dict, state: dict):
    state["taken"] = state["taken"] if state.get("taken", False) else 0
    if len(args) and state["taken"] == args[0]:
        state["taken"] = 0 # this allows us to reuse the query later
        return "done" # closes all previous pipes
        
    if not gremlin or not isinstance(gremlin, dict):
        return PULL

    state["taken"] += 1
    return gremlin

def addAsPipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not gremlin:
        return PULL

    if not len(args):
        error("as pipe missing argument(s)")
        return "done"

    gremlin["state"]["as"] = gremlin["state"]["as"] if gremlin["state"].get("as", False) else {}
    gremlin["state"]["as"][args[0]] = gremlin["vertex"]
    return gremlin

def addMergePipetype(graph: Graph, args, gremlin: dict, state: dict):
    if not state.get("vertices", False) and not gremlin:
        return PULL

    if not state.get("vertices", False) or not len(state["vertices"]):
        gr_state = gremlin["state"] if gremlin.get("state", False) else {}
        obj = gr_state["as"] if gr_state.get("as", False) else {}

        # check if each argument (as rename) exists in obj dict
        mappedArguements = list(map(lambda id: obj.get(id, False), args)) 
        # filter the vertices we can find that match
        state["vertices"] = list(filter(lambda id: True if id else False, mappedArguements))

    if not len(state["vertices"]):
        return PULL

    vertex = state["vertices"].pop()

    if isinstance(gremlin, dict):
        return Graf["makeGremlin"](vertex, gremlin["state"])
    else:
        return Graf["makeGremlin"](vertex, False)

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

# register all the pipetypes our query will accept
Graf["addPipetype"]("vertex", addVertexPipetype)
Graf["addPipetype"]("from", Graf["simpleTraversal"]("from"))
Graf["addPipetype"]("to", Graf["simpleTraversal"]("to"))
Graf["addPipetype"]("property", addPropertyPipetype)
Graf["addPipetype"]("unique", addUniquePipetype)
Graf["addPipetype"]("filter", addFilterPipetype)
Graf["addPipetype"]("take", addTakePipetype)
Graf["addPipetype"]("as", addAsPipetype)
Graf["addPipetype"]("merge", addMergePipetype)
Graf["addPipetype"]("except", addExceptPipetype)
Graf["addPipetype"]("back", addBackPipetype)

def showProg(prog: list):
    final = " "
    for s in prog:
        final += s[0]
        final += '('
        if s[1]:
            args = s[1][0]
            if isinstance(args, str):
                final += ', '.join(s[1])
            elif isinstance(args, list):
                final += ', '.join(args)
            elif isinstance(args, dict):
                final += json.dumps(args)
            elif callable(args) or isfunction(args):
                final += f"<:function:>"
            elif isinstance(args, int):
                final += str(args)
        final += ').'
    print("-?>", " "+final[0:len(final)-1])

def addTransformer(fn, priority: int):
    if not isfunction(fn) or not callable(fn):
        return error("Invalid transformer function")
    ind = 0
    for i in range(len(Graf["Transformers"])):
        if priority > Graf["Transformers"][i]["priority"]:
            ind = i
            break
        Graf["Transformers"].insert(i, {"priority": priority, "fn": fn})

def transform(program):
    acc = program[:]
    for transformer in Graf["Transformers"]:
        acc = transformer["fn"](acc)
    return acc
        
Graf["Transformers"] = []
Graf["addTransformer"] = addTransformer