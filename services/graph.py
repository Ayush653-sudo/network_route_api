import heapq
from collections import defaultdict
from sqlalchemy.orm import Session
from models import Edge


def build_graph(db: Session) -> dict[str, list[tuple[float, str]]]:
    graph: dict[str, list[tuple[float, str]]] = defaultdict(list)
    edges = db.query(Edge).all()
    for edge in edges:
        src = edge.source_node.name
        dst = edge.destination_node.name
        graph[src].append((edge.latency, dst))
    return graph


def dijkstra(
    graph: dict[str, list[tuple[float, str]]],
    source: str,
    destination: str,
) -> tuple[float, list[str]] | None:
    heap: list[tuple[float, str, list[str]]] = [(0.0, source, [source])]
    visited: set[str] = set()

    while heap:
        cost, node, path = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)

        if node == destination:
            return cost, path

        for edge_latency, neighbour in graph.get(node, []):
            if neighbour not in visited:
                heapq.heappush(heap, (cost + edge_latency, neighbour, path + [neighbour]))

    return None
