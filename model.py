class Entity:
    def __init__(p, name, props=None) -> None:
        p.name = name
        p.props = props
    
    def toNode(p) -> dict:
        node = {}
        node["id"] = p.name
        node["from"] = []
        node["to"] = []

        if p.props:
            node.update(p.props)
        return node

class Connection:
    def __init__(f, A: Entity, B: Entity, ctype: str, isTwoWay: bool, props: dict=None) -> None:
        f.A = A
        f.B = B
        f.connection = ctype
        f.isTwoway = isTwoWay
        f.props = props

    def toEdges(f) -> list[dict]:
        nodeA = f.A.toNode()
        nodeB = f.B.toNode()

        edgeAtoB = {"label": f.connection}

        # handle connection from A to B
        edgeAtoB["from"] = nodeA["id"]
        edgeAtoB["to"] = nodeB["id"]
        if f.props:
            edgeAtoB.update(f.props)
            
        if f.isTwoway:
            edgeBtoA = {"label": f.connection}

            # handle connection from B to A
            edgeBtoA["from"] = nodeB["id"]
            edgeBtoA["to"] = nodeA["id"]

            if f.props:
                edgeBtoA.update(f.props)

            return [edgeAtoB, edgeBtoA]
        return [edgeAtoB]

