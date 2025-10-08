#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
profiling.py
------------
Scripts auxiliares para medir rendimiento y memoria.

Uso sugerido:
- cProfile (guardar y ver stats):
    python -m cProfile -o profile.out ventas.py analizar ventas.csv
    python - <<'PY'
import pstats
p = pstats.Stats('profile.out')
p.sort_stats('cumtime').print_stats(20)
PY

- line_profiler (kernprof):
    pip install line_profiler
    kernprof -l -v ventas.py analizar ventas.csv

- memory_profiler:
    pip install memory_profiler
    python -m memory_profiler ventas.py analizar ventas.csv

- timeit (micro-bench local):
    python profiling.py --timeit
"""
import argparse
import timeit


def run_timeit():
    setup = "from ventas import generar_csv_ventas, analizar_ventas_streaming; generar_csv_ventas('ventas.csv', 10000)"
    stmt = "analizar_ventas_streaming('ventas.csv')"
    reps = 5
    t = timeit.timeit(stmt=stmt, setup=setup, number=reps)
    print(f"[timeit] {reps} ejecuciones -> {t:.4f}s total; {t/reps:.6f}s por run")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeit", action="store_true", help="Corre un micro-benchmark con timeit")
    args = ap.parse_args()

    if args.timeit:
        run_timeit()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
