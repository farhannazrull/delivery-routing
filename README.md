# Smart Delivery Routing — Dijkstra vs. Bellman-Ford

EF234405 Design & Analysis of Algorithms — Final Exam (Group Capstone Project)

A courier-routing tool that models a city as a weighted directed graph and
finds the fastest route from a depot to delivery stops, using two
from-scratch shortest-path algorithms:

- **Algorithm A — Dijkstra** (binary min-heap), the fast production
  algorithm for non-negative travel times.
- **Algorithm B — Bellman-Ford** (edge relaxation), the general-purpose
  baseline: simpler, also correct on negative edge weights (e.g. toll
  rebates), and used here as the correctness cross-check for Dijkstra.

Both algorithms run on the **same** graph instances; their shortest-path
distances must agree everywhere (and do — see `tests/` and the benchmark
output), which is the project's "Comparable" requirement.

## Repository layout

```
src/
  graph.py          Graph data structure + synthetic road-network generator
  dijkstra.py        Algorithm A (binary heap, implemented from scratch)
  bellman_ford.py     Algorithm B (edge relaxation, implemented from scratch)
demo/
  cli_demo.py         End-to-end delivery-routing demo (prints routes, saves a map PNG)
bench/
  run_benchmark.py    ONE-COMMAND benchmark harness -> benchmark_results.csv
  plot_results.py     Produces the runtime-vs-size log-log plot + growth exponent
tests/
  test_correctness.py Unit tests + A-vs-B cross-check tests
docs/
  architecture.png    Module/architecture diagram
report/
  Report.pdf           Full write-up (design, analysis, evaluation, conclusion)
```

## Requirements

- Python 3.10+
- `pip install -r requirements.txt` (numpy, scipy, matplotlib — used only
  for graph generation, plotting, and timing; **no shortest-path library is
  used anywhere** — see "Own the core" note below)

## How to run

```bash
git clone <this repo URL>
cd delivery-routing
pip install -r requirements.txt

# 1. Run correctness tests
python -m pytest tests/ -v
# (or: python tests/test_correctness.py)

# 2. Run the end-to-end demo (depot -> several delivery stops)
python demo/cli_demo.py --n 1500 --stops 6 --seed 1
# -> prints each route + timing, saves demo/demo_map.png

# 3. Reproduce the full benchmark (ONE COMMAND, the required entry point)
python bench/run_benchmark.py
# -> writes bench/benchmark_results.csv (5 sizes: 100..10,000 vertices, 5 repeats each, fixed seeds)

python bench/plot_results.py
# -> writes bench/runtime_vs_size.png and prints the empirical growth exponent
```

All randomness is seeded (`MASTER_SEED = 42` in `bench/run_benchmark.py`,
`--seed` flag in the demo), so every run reproduces identical graphs and
(modulo machine-dependent timing noise) comparable results.

## "Own the core" statement

Per the assignment's technical constraints, the core algorithmic logic of
both Dijkstra (`src/dijkstra.py`) and Bellman-Ford (`src/bellman_ford.py`)
is entirely hand-written: no `networkx`, no `scipy.sparse.csgraph`, no
graph library's shortest-path function is called anywhere in this
repository. Libraries are used only for supporting roles:

| Library | Role |
|---|---|
| `heapq` (Python stdlib) | priority-queue *container* inside our own Dijkstra logic (push/pop only — decrease-key, relaxation, and visited-tracking are hand-written) |
| `scipy.spatial.cKDTree` | nearest-neighbor *queries* used only to build the synthetic road-network graph (not used for shortest paths) |
| `numpy` | random number generation and vectorized distance math for graph generation/plotting |
| `matplotlib` | plotting only |

## Attribution

- Dijkstra's algorithm: E. W. Dijkstra, "A note on two problems in
  connexion with graphs," *Numerische Mathematik*, 1959.
- Bellman-Ford algorithm: R. Bellman (1958); L. R. Ford Jr. (1956).
- `scipy.spatial.cKDTree` — SciPy documentation, https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html
- Course material: EF234405 Design & Analysis of Algorithms lecture notes (2025/2026-2).

## Authors

Single-member submission — see `Report.pdf` (title page) and the
contribution table in `Report.pdf` §4 for details.
