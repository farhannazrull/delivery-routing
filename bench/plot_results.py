"""
bench/plot_results.py
-----------------------
Reads bench/benchmark_results.csv (produced by run_benchmark.py) and:
  1. Plots runtime vs. n on log-log axes for both algorithms
     (bench/runtime_vs_size.png) -- one plot containing both curves so the
     crossover/gap is directly visible, as required by A4.
  2. Estimates the empirical growth exponent of each algorithm via a
     least-squares fit of log(time) vs log(n) (slope of the line), and
     prints how that compares to the theoretical complexity derived in
     the report (A5: theory vs. practice).

This script only does plotting/curve-fitting (numpy.polyfit, matplotlib) --
no shortest-path logic lives here.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "benchmark_results.csv")
OUT_PNG = os.path.join(HERE, "runtime_vs_size.png")


def load_csv():
    rows = []
    with open(CSV_PATH) as f:
        for r in csv.DictReader(f):
            rows.append(
                dict(
                    n=int(r["n"]),
                    edges=int(r["edges"]),
                    dijkstra=float(r["dijkstra_ms_mean"]),
                    bellman_ford=float(r["bellman_ford_ms_mean"]),
                )
            )
    return rows


def growth_exponent(ns, ts):
    """Slope of log(t) vs log(n): t ~ n^slope."""
    log_n = np.log(ns)
    log_t = np.log(ts)
    slope, intercept = np.polyfit(log_n, log_t, 1)
    return slope


def main():
    rows = load_csv()
    ns = np.array([r["n"] for r in rows], dtype=float)
    d_t = np.array([r["dijkstra"] for r in rows], dtype=float)
    bf_t = np.array([r["bellman_ford"] for r in rows], dtype=float)
    edges = np.array([r["edges"] for r in rows], dtype=float)

    d_slope = growth_exponent(ns, d_t)
    bf_slope = growth_exponent(ns, bf_t)

    # Theoretical reference curves, scaled to match the first data point so
    # they overlay nicely: Dijkstra ~ (n+m) log n ; Bellman-Ford ~ n * m
    theory_dijkstra = ns * np.log2(ns)  # E = O(n) here (sparse k-NN graph), so (V+E)logV ~ n log n
    theory_dijkstra *= d_t[0] / theory_dijkstra[0]

    theory_bf = ns * edges
    theory_bf *= bf_t[0] / theory_bf[0]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.loglog(ns, d_t, "o-", color="#2E75B6", linewidth=2, markersize=7, label="Dijkstra (measured)")
    ax.loglog(ns, bf_t, "s-", color="#C0392B", linewidth=2, markersize=7, label="Bellman-Ford (measured)")
    ax.loglog(ns, theory_dijkstra, "--", color="#2E75B6", alpha=0.5, label=r"$O((V+E)\log V)$ reference")
    ax.loglog(ns, theory_bf, "--", color="#C0392B", alpha=0.5, label=r"$O(V \cdot E)$ reference")

    ax.set_xlabel("Number of vertices, n (log scale)")
    ax.set_ylabel("Mean running time, ms (log scale, 5-run avg)")
    ax.set_title("Runtime vs. input size: Dijkstra vs. Bellman-Ford")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=160)
    print(f"Saved plot to {OUT_PNG}")

    print(f"\nEmpirical growth exponent (slope of log-log fit):")
    print(f"  Dijkstra:      t ~ n^{d_slope:.2f}")
    print(f"  Bellman-Ford:  t ~ n^{bf_slope:.2f}")


if __name__ == "__main__":
    main()
