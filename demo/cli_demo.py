"""
demo/cli_demo.py
------------------
End-to-end demo application (the "(I3) end-to-end application/demo" rubric
item): a toy Smart Delivery Routing planner.

Scenario: a courier depot needs the fastest route to each of several
delivery addresses in a city of n intersections. The tool:
  1. Generates (or you can point it at) a road network.
  2. Runs Dijkstra AND Bellman-Ford from the depot.
  3. Prints, for every delivery stop: total travel time, the route, and
     which algorithm computed it -- plus confirms the two algorithms agree.
  4. Saves a map visualization (PNG) of the city with the depot, the
     delivery stops, and the shortest-path tree highlighted.

Usage:
    python demo/cli_demo.py --n 1500 --stops 6 --seed 1
"""

import os
import sys
import argparse
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import matplotlib.pyplot as plt
from graph import generate_road_network
from dijkstra import dijkstra, reconstruct_path as d_path
from bellman_ford import bellman_ford, reconstruct_path as bf_path

HERE = os.path.dirname(__file__)


def main():
    ap = argparse.ArgumentParser(description="Smart Delivery Routing demo")
    ap.add_argument("--n", type=int, default=1500, help="number of intersections")
    ap.add_argument("--k", type=int, default=6, help="k nearest-neighbor road connections")
    ap.add_argument("--stops", type=int, default=6, help="number of delivery stops")
    ap.add_argument("--seed", type=int, default=1, help="random seed (reproducible)")
    ap.add_argument("--depot", type=int, default=0, help="vertex id of the depot")
    ap.add_argument("--out", type=str, default=os.path.join(HERE, "demo_map.png"))
    args = ap.parse_args()

    print(f"Generating road network: n={args.n}, k_neighbors={args.k}, seed={args.seed}")
    graph, coords = generate_road_network(args.n, k_neighbors=args.k, seed=args.seed)
    print(f"  -> {graph.num_vertices} intersections, {graph.num_edges} directed road segments\n")

    import random
    rng = random.Random(args.seed)
    stops = rng.sample([v for v in range(args.n) if v != args.depot], args.stops)

    t0 = time.perf_counter()
    d_dist, d_parent = dijkstra(graph, args.depot)
    t1 = time.perf_counter()
    bf_dist, bf_parent, neg = bellman_ford(graph, args.depot)
    t2 = time.perf_counter()

    print(f"Depot: intersection #{args.depot}")
    print(f"Dijkstra time:      {(t1 - t0) * 1000:.3f} ms")
    print(f"Bellman-Ford time:  {(t2 - t1) * 1000:.3f} ms")
    print(f"Negative cycle detected: {neg}\n")

    print(f"{'Stop':>6} {'Dijkstra time':>14} {'B-F time':>10} {'Match':>7}  Route (first..last 3 hops)")
    print("-" * 80)
    routes = {}
    for s in stops:
        a, b = d_dist[s], bf_dist[s]
        match = (a == b) or (a != float("inf") and b != float("inf") and abs(a - b) < 1e-6)
        path = d_path(d_parent, args.depot, s)
        routes[s] = path
        if path is None:
            route_str = "UNREACHABLE"
        elif len(path) <= 6:
            route_str = " -> ".join(map(str, path))
        else:
            route_str = " -> ".join(map(str, path[:3])) + " -> ... -> " + " -> ".join(map(str, path[-3:]))
        print(f"{s:>6} {a:>14.3f} {b:>10.3f} {str(match):>7}  {route_str}")

    # --- visualization -----------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(coords[:, 0], coords[:, 1], s=4, color="#bbbbbb", zorder=1, label="intersections")
    for u, lst in graph.adj.items():
        for v, _w in lst:
            ax.plot(
                [coords[u, 0], coords[v, 0]],
                [coords[u, 1], coords[v, 1]],
                color="#dddddd",
                linewidth=0.3,
                zorder=1,
            )
    colors = plt.cm.tab10.colors
    for i, s in enumerate(stops):
        path = routes[s]
        if path is None:
            continue
        xs = [coords[v, 0] for v in path]
        ys = [coords[v, 1] for v in path]
        ax.plot(xs, ys, color=colors[i % len(colors)], linewidth=2.2, zorder=3, label=f"route to stop {s}")
        ax.scatter([coords[s, 0]], [coords[s, 1]], color=colors[i % len(colors)], s=60, zorder=4, edgecolor="black")

    ax.scatter([coords[args.depot, 0]], [coords[args.depot, 1]], color="black", marker="*", s=220, zorder=5, label="depot")
    ax.set_title(f"Smart Delivery Routing demo (n={args.n} intersections)")
    ax.legend(loc="upper left", fontsize=7, framealpha=0.9)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(args.out, dpi=160)
    print(f"\nMap saved to {args.out}")


if __name__ == "__main__":
    main()
