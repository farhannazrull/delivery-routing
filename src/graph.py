"""
graph.py
--------
Core data structure for a weighted, directed graph used to model a road
network for the Smart Delivery Routing project.

Representation: adjacency list.
    self.adj[u] = list of (v, w) meaning there is a directed road segment
    u -> v with travel-time weight w.

This module ALSO contains the synthetic road-network generator used for the
benchmark sweep. The generator uses scipy.spatial.cKDTree purely as a
*supporting* spatial-indexing structure to build a realistic sparse graph
quickly at large n (n up to 10,000+). It is NOT used to compute shortest
paths -- the shortest-path algorithms in dijkstra.py and bellman_ford.py are
implemented entirely from scratch.
"""

from __future__ import annotations
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

import numpy as np
from scipy.spatial import cKDTree


@dataclass
class Graph:
    """Weighted directed graph, adjacency-list representation."""

    n: int
    adj: Dict[int, List[Tuple[int, float]]] = field(default_factory=dict)

    def __post_init__(self):
        for v in range(self.n):
            self.adj.setdefault(v, [])

    def add_edge(self, u: int, v: int, w: float) -> None:
        self.adj[u].append((v, w))

    def add_undirected_edge(self, u: int, v: int, w: float) -> None:
        """Two directed arcs of the same weight (used for symmetric segments)."""
        self.add_edge(u, v, w)
        self.add_edge(v, u, w)

    @property
    def num_vertices(self) -> int:
        return self.n

    @property
    def num_edges(self) -> int:
        return sum(len(es) for es in self.adj.values())

    def edges(self):
        """Yield every directed edge (u, v, w)."""
        for u, lst in self.adj.items():
            for v, w in lst:
                yield u, v, w

    def neighbors(self, u: int):
        return self.adj[u]


def _make_weakly_connected(graph: Graph, coords: np.ndarray, rng: random.Random) -> None:
    """
    Ensure the graph is connected (treating edges as undirected for the
    purposes of this check) by repeatedly linking the nearest pair of
    vertices across the two largest disconnected components.

    Simple union-find based component finder, then bridge components with a
    single (bidirectional, low-weight) edge based on Euclidean distance.
    """
    parent = list(range(graph.n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for u, v, _ in graph.edges():
        union(u, v)

    components: Dict[int, List[int]] = {}
    for v in range(graph.n):
        components.setdefault(find(v), []).append(v)

    comp_list = list(components.values())
    if len(comp_list) <= 1:
        return

    # Bridge every extra component to the largest one via the closest pair
    # of nodes (cheap O(k * m) where k = #components, m = size of pieces;
    # fine since disconnected components are rare with a reasonable k-NN).
    comp_list.sort(key=len, reverse=True)
    main = comp_list[0]
    main_coords = coords[main]
    for comp in comp_list[1:]:
        comp_coords = coords[comp]
        # brute-force closest pair between the two small sets
        best = None
        for i, a in enumerate(comp):
            d = np.sum((main_coords - comp_coords[i]) ** 2, axis=1)
            j = int(np.argmin(d))
            dist = math.sqrt(float(d[j]))
            if best is None or dist < best[0]:
                best = (dist, a, main[j])
        dist, a, b = best
        w = round(dist * (0.9 + 0.2 * rng.random()), 3)
        graph.add_undirected_edge(a, b, max(w, 0.01))
        main.append(a)
        main_coords = coords[main]


def generate_road_network(
    n: int,
    k_neighbors: int = 6,
    seed: int = 42,
    asymmetry: float = 0.35,
) -> Graph:
    """
    Generate a synthetic but realistic sparse road network with n
    intersections (vertices).

    Method: scatter n points uniformly in a unit square (representing
    intersections on a map), connect each point to its k_neighbors nearest
    neighbors (a standard way to build a sparse, planar-ish, realistic
    "road graph"), and weight each edge by Euclidean distance perturbed by
    a random "traffic" multiplier. A fraction of edges (controlled by
    `asymmetry`) get a different forward/backward weight to model one-way
    streets / asymmetric traffic, which is why the graph is directed.

    All randomness is seeded for reproducibility.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    coords = np_rng.random((n, 2)) * 100.0  # 100x100 "km" map
    tree = cKDTree(coords)

    graph = Graph(n)
    # k+1 because the nearest neighbor of a point is itself (distance 0)
    k = min(k_neighbors + 1, n)
    dists, idxs = tree.query(coords, k=k)

    seen = set()
    for u in range(n):
        for dist, v in zip(dists[u], idxs[u]):
            v = int(v)
            if v == u:
                continue
            key = (min(u, v), max(u, v))
            if key in seen:
                continue
            seen.add(key)

            base_w = max(float(dist), 0.01)
            traffic_mult_fwd = 0.8 + 0.6 * rng.random()
            graph.add_edge(u, v, round(base_w * traffic_mult_fwd, 3))

            if rng.random() < asymmetry:
                traffic_mult_bwd = 0.8 + 0.6 * rng.random()
                graph.add_edge(v, u, round(base_w * traffic_mult_bwd, 3))
            else:
                graph.add_edge(v, u, round(base_w * traffic_mult_fwd, 3))

    _make_weakly_connected(graph, coords, rng)
    return graph, coords


def generate_negative_edge_demo(seed: int = 7) -> Graph:
    """
    Small hand-sized DAG-like graph used ONLY in the qualitative
    discussion of Bellman-Ford's generality (Report sec. 3, A1/A3): a few
    edges carry a *negative* weight, modelling a toll-rebate / EV-fast-lane
    incentive that effectively pays the courier back a fraction of the
    travel cost on certain segments. The graph is constructed so it
    provably contains NO negative cycle (edges only go "forward" in a
    topological order), so Bellman-Ford's shortest paths are well defined.
    Dijkstra is NOT valid on this graph and is intentionally not run on it.
    """
    g = Graph(6)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 2)
    g.add_edge(1, 2, -3)   # rebate segment
    g.add_edge(1, 3, 5)
    g.add_edge(2, 3, 7)
    g.add_edge(2, 4, -1)   # rebate segment
    g.add_edge(3, 5, 2)
    g.add_edge(4, 3, 1)
    g.add_edge(4, 5, 6)
    return g
