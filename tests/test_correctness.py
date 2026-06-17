"""
tests/test_correctness.py
--------------------------
Unit tests for Algorithm A (Dijkstra) and Algorithm B (Bellman-Ford).

Strategy:
  1. Hand-built tiny graphs with known, hand-computed shortest distances --
     each algorithm is checked against the hand-computed ground truth.
  2. Cross-check: on every non-negative random instance, Dijkstra and
     Bellman-Ford must agree on every distance (this is the "Comparable"
     mandatory requirement -- both solve the same instance and we verify
     they produce the same answer).
  3. A negative-cycle instance to confirm Bellman-Ford correctly detects it
     and refuses to report distances.

Run with:  python -m pytest tests/ -v   (from the repo root)
"""

import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from graph import Graph, generate_road_network, generate_negative_edge_demo
from dijkstra import dijkstra
from bellman_ford import bellman_ford


def test_small_hand_graph():
    # 0 -> 1 (4), 0 -> 2 (1), 2 -> 1 (1), 1 -> 3 (1), 2 -> 3 (5)
    # Shortest 0->1 should be via 2: 1+1 = 2 (not the direct edge, weight 4)
    g = Graph(4)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 2, 1)
    g.add_edge(2, 1, 1)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 5)

    expected = [0, 2, 1, 3]

    d_dist, _ = dijkstra(g, 0)
    bf_dist, bf_parent, neg = bellman_ford(g, 0)

    assert d_dist == expected, f"Dijkstra wrong: {d_dist}"
    assert not neg
    assert bf_dist == expected, f"Bellman-Ford wrong: {bf_dist}"


def test_unreachable_vertex():
    g = Graph(3)
    g.add_edge(0, 1, 2)
    # vertex 2 has no incoming edge from 0
    d_dist, _ = dijkstra(g, 0)
    bf_dist, _, neg = bellman_ford(g, 0)
    assert d_dist[2] == float("inf")
    assert bf_dist[2] == float("inf")
    assert not neg


def test_cross_check_on_random_instances():
    """The mandatory 'Comparable' requirement: both algorithms must agree
    on every non-negative instance."""
    for size in (20, 50, 200):
        g, _ = generate_road_network(size, k_neighbors=5, seed=size)
        d_dist, _ = dijkstra(g, 0)
        bf_dist, _, neg = bellman_ford(g, 0)
        assert not neg
        for v in range(size):
            a, b = d_dist[v], bf_dist[v]
            if a == float("inf") or b == float("inf"):
                assert a == b
            else:
                assert abs(a - b) < 1e-6, f"mismatch at size={size}, v={v}: {a} vs {b}"


def test_negative_cycle_detected():
    g = Graph(3)
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, -3)
    g.add_edge(2, 0, 1)  # cycle 0->1->2->0 has weight 1-3+1 = -1 < 0
    _, _, neg = bellman_ford(g, 0)
    assert neg


def test_negative_edges_without_cycle():
    """Bellman-Ford handles negative weights fine as long as there's no
    negative cycle -- this is exactly the capability Dijkstra lacks."""
    g = generate_negative_edge_demo()
    dist, parent, neg = bellman_ford(g, 0)
    assert not neg
    # hand-checked shortest distances for generate_negative_edge_demo()
    # 0->1:4, 0->2: min(2, 4-3)=1, 0->3: min(1+5, 1+7, (4-1)+1)=4 via 1->2->4->3
    assert dist[1] == 4
    assert dist[2] == 1
    assert dist[4] == 0  # 0->2->4 = 1 + (-1) = 0
    assert dist[3] == 1  # 0->2->4->3 = 1 + (-1) + 1 = 1


def test_dijkstra_rejects_negative_weight():
    g = Graph(2)
    g.add_edge(0, 1, -5)
    try:
        dijkstra(g, 0)
        assert False, "Dijkstra should have raised on a negative edge"
    except ValueError:
        pass


if __name__ == "__main__":
    test_small_hand_graph()
    test_unreachable_vertex()
    test_cross_check_on_random_instances()
    test_negative_cycle_detected()
    test_negative_edges_without_cycle()
    test_dijkstra_rejects_negative_weight()
    print("All correctness tests passed.")
