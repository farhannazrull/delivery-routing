"""
dijkstra.py
-----------
Algorithm A: Dijkstra's single-source shortest-path algorithm with a binary
min-heap, implemented FROM SCRATCH (only `heapq` is used as a supporting
priority-queue container; all relaxation / decrease-key / pop-min logic
below is hand-written, not a library shortest-path call).

Precondition: all edge weights must be >= 0. (We assert this explicitly --
this precondition, and what happens when it is violated, is exactly the
property Bellman-Ford does not require; see the Analysis section.)
"""

from __future__ import annotations
import heapq
from typing import List, Tuple, Optional
from graph import Graph

INF = float("inf")


def dijkstra(graph: Graph, source: int) -> Tuple[List[float], List[Optional[int]]]:
    """
    Returns (dist, parent):
        dist[v]   = length of the shortest path from source to v (INF if
                    unreachable)
        parent[v] = predecessor of v on that shortest path (None if v is
                    the source or unreachable)

    Implementation notes (own code, not a library call):
      * We do not support a true decrease-key on Python's heapq, so we use
        the standard "lazy deletion" trick: push a new (dist, vertex) pair
        every time we find a strictly better distance, and when popping,
        discard any entry that is now stale (dist[v] has since improved).
      * Each vertex is "finalized" (settled) at most once -- the moment it
        is popped with an up-to-date distance -- which is what gives the
        O((V + E) log V) bound derived in the report.
    """
    n = graph.num_vertices
    dist = [INF] * n
    parent: List[Optional[int]] = [None] * n
    visited = [False] * n

    dist[source] = 0.0
    pq: List[Tuple[float, int]] = [(0.0, source)]

    while pq:
        d_u, u = heapq.heappop(pq)
        if visited[u]:
            continue  # stale entry, skip (lazy deletion)
        if d_u > dist[u]:
            continue  # stale entry, skip
        visited[u] = True

        for v, w in graph.neighbors(u):
            if w < 0:
                raise ValueError(
                    f"Dijkstra precondition violated: negative edge weight "
                    f"({u} -> {v}, w={w}). Use Bellman-Ford for this graph."
                )
            if visited[v]:
                continue
            new_d = d_u + w
            if new_d < dist[v]:
                dist[v] = new_d
                parent[v] = u
                heapq.heappush(pq, (new_d, v))

    return dist, parent


def reconstruct_path(parent: List[Optional[int]], source: int, target: int) -> Optional[List[int]]:
    """Walk parent pointers from target back to source. None if unreachable."""
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
