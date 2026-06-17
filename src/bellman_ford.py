"""
bellman_ford.py
----------------
Algorithm B: Bellman-Ford single-source shortest-path algorithm,
implemented FROM SCRATCH. No special data structure is required beyond a
plain edge list, which is exactly the point of including it as the
baseline / cross-check: it is simpler than Dijkstra, works on graphs with
negative edge weights (as long as there is no negative cycle), and can
detect a negative cycle if one exists -- at the cost of being
asymptotically slower, O(V*E) vs Dijkstra's O((V+E) log V).
"""

from __future__ import annotations
from typing import List, Tuple, Optional
from graph import Graph

INF = float("inf")


def bellman_ford(
    graph: Graph, source: int
) -> Tuple[List[float], List[Optional[int]], bool]:
    """
    Returns (dist, parent, has_negative_cycle).

    Standard relaxation: repeat |V|-1 times, relax every edge. If, on one
    extra (|V|-th) pass, any edge can still be relaxed, the graph contains
    a negative-weight cycle reachable from source and shortest paths are
    undefined; we report that via has_negative_cycle=True instead of
    returning bogus distances.
    """
    n = graph.num_vertices
    dist = [INF] * n
    parent: List[Optional[int]] = [None] * n
    dist[source] = 0.0

    edge_list = list(graph.edges())  # materialize once, reused every round

    for _ in range(n - 1):
        changed = False
        for u, v, w in edge_list:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break  # early exit: no edge relaxed this round -> converged

    has_negative_cycle = False
    for u, v, w in edge_list:
        if dist[u] != INF and dist[u] + w < dist[v]:
            has_negative_cycle = True
            break

    return dist, parent, has_negative_cycle


def reconstruct_path(parent: List[Optional[int]], source: int, target: int) -> Optional[List[int]]:
    if parent[target] is None and target != source:
        return None
    path = [target]
    while path[-1] != source:
        p = parent[path[-1]]
        if p is None:
            return None
        path.append(p)
    path.reverse()
    return path
