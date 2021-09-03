from graph import error, Graph

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

Pipetypes = {}

def fauxPipetype(_, __, maybe_gremlin):
    return maybe_gremlin if maybe_gremlin else "pull"

def addPipetype(name: str, fn, query: Query):
    Pipetypes[name] = fn
    # Query.
    # query.add(name, )

def getPipetype(name: str):
    pipetype = Pipetypes.get(name, None)

    if not pipetype:
        error(f"Unrecognized pipetype {name}")
        return fauxPipetype

    return pipetype