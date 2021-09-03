class Query:
    def __init__(q, graph) -> None:
        q.graph = graph
        q.state = []
        q.program = []
        q.gremlins = []

    def add(q, pipetype, args):
        step = [pipetype, args]
        q.program.append(step)
        return q