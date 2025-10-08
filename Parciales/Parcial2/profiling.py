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
