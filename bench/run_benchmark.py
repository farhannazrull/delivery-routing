"""
bench/run_benchmark.py
-----------------------
ONE-COMMAND benchmark harness (the required reproducibility entry point).

Usage:
    python bench/run_benchmark.py

What it does:
  * Generates 5 synthetic road-network instances with n = 100, 300, 1000,
    3000, 10000 vertices (random seed fixed per size -> fully
    reproducible), spanning two orders of magnitude (10^2 -> 10^4).
  * Times Dijkstra and Bellman-Ford on the SAME instance (5 repeats each,
    mean +/- std reported, to smooth out OS/timing jitter).
  * Cross-checks that both algorithms report identical shortest-path
    distances on every instance (the mandatory "Comparable" requirement).
  * Writes results to bench/benchmark_results.csv.

This script contains NO algorithmic logic of its own -- it only calls the
from-scratch implementations in src/dijkstra.py and src/bellman_ford.py and
measures wall-clock time with Python's time.perf_counter (a "supporting"
timing facility, not a shortest-path library).
"""

import os
import sys
import csv
import time
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from graph import generate_road_network
from dijkstra import dijkstra
from bellman_ford import bellman_ford

SIZES = [100, 300, 1000, 3000, 10000]
K_NEIGHBORS = 6
REPEATS = 5
MASTER_SEED = 42  # fixed seed -> reproducible graphs across runs/machines
SOURCE = 0

OUT_CSV = os.path.join(os.path.dirname(__file__), "benchmark_results.csv")


def time_fn(fn, repeats=REPEATS):
    times = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)  # ms
    return result, statistics.mean(times), (statistics.stdev(times) if len(times) > 1 else 0.0)


def main():
    rows = []
    print(f"{'n':>7} {'edges':>8} {'Dijkstra (ms)':>16} {'Bellman-Ford (ms)':>20} {'match':>7}")
    print("-" * 65)

    for n in SIZES:
        seed = MASTER_SEED + n  # distinct but reproducible per size
        graph, _coords = generate_road_network(n, k_neighbors=K_NEIGHBORS, seed=seed)
        m = graph.num_edges

        (d_dist, _), d_mean, d_std = time_fn(lambda: dijkstra(graph, SOURCE))
        (bf_dist, _, neg), bf_mean, bf_std = time_fn(lambda: bellman_ford(graph, SOURCE))

        assert not neg, "unexpected negative cycle in a non-negative benchmark graph"

        match = all(
            (a == b) or (a != float("inf") and b != float("inf") and abs(a - b) < 1e-6)
            for a, b in zip(d_dist, bf_dist)
        )

        rows.append(
            dict(
                n=n,
                edges=m,
                seed=seed,
                dijkstra_ms_mean=round(d_mean, 4),
                dijkstra_ms_std=round(d_std, 4),
                bellman_ford_ms_mean=round(bf_mean, 4),
                bellman_ford_ms_std=round(bf_std, 4),
                distances_match=match,
            )
        )
        print(f"{n:>7} {m:>8} {d_mean:>16.4f} {bf_mean:>20.4f} {str(match):>7}")

    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to {OUT_CSV}")


if __name__ == "__main__":
    main()
