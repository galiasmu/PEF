#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
profiling.py
------------
Scripts auxiliares para medir rendimiento y memoria.

Herramientas incluidas:
- cProfile: Análisis de tiempo por función
- timeit: Micro-benchmarks de rendimiento
- Comparación Streaming vs Pandas

Uso:
    python profiling.py --cprofile      # Ejecutar cProfile
    python profiling.py --timeit        # Ejecutar timeit
    python profiling.py --all           # Ejecutar todo
"""
import argparse
import cProfile
import pstats
import timeit
import os
from ventas import generar_csv_ventas, analizar_ventas_streaming, analizar_ventas_pandas


def verificar_o_generar_datos(archivo="ventas.csv", num_registros=10000):
    """Verifica si existe el archivo de datos, si no lo genera"""
    try:
        with open(archivo, 'r') as f:
            # Contar líneas para verificar
            lineas = sum(1 for _ in f) - 1  # -1 por header
            print(f"Archivo '{archivo}' encontrado con {lineas:,} registros.")
            return lineas
    except FileNotFoundError:
        print(f"Generando archivo '{archivo}' con {num_registros:,} registros...")
        generar_csv_ventas(archivo, num_registros, seed=42)
        print(f"Archivo '{archivo}' generado.")
        return num_registros


def run_cprofile(archivo="ventas.csv", chunksize=5000):
    """Ejecuta cProfile para ambas estrategias"""
    print("\n" + "=" * 70)
    print("PROFILING CON cProfile")
    print("=" * 70)

    verificar_o_generar_datos(archivo)

    # --- STREAMING ---
    print("\n🌊Ejecutando análisis con cProfile (modo STREAMING)...")

    # Método 1: Guardar resultados en archivo .out
    cProfile.run(
        f"analizar_ventas_streaming('{archivo}')",
        "profile_streaming.out"
    )

    # Método 2: Guardar en formato .prof para visualización con snakeviz
    profiler_stream = cProfile.Profile()
    profiler_stream.enable()
    analizar_ventas_streaming(archivo)
    profiler_stream.disable()
    profiler_stream.dump_stats("resultado_streaming.prof")

    # --- PANDAS ---
    print(f"\n📦 Ejecutando análisis con cProfile (modo PANDAS, chunksize={chunksize:,})...")

    cProfile.run(
        f"analizar_ventas_pandas('{archivo}', chunksize={chunksize})",
        "profile_pandas.out"
    )

    profiler_pandas = cProfile.Profile()
    profiler_pandas.enable()
    analizar_ventas_pandas(archivo, chunksize=chunksize)
    profiler_pandas.disable()
    profiler_pandas.dump_stats("resultado_pandas.prof")

    # --- MOSTRAR RESULTADOS ---
    print("\n" + "=" * 70)
    print("📊 RESULTADOS - STREAMING (Top 15 funciones por tiempo acumulado)")
    print("=" * 70)
    stats_stream = pstats.Stats("profile_streaming.out")
    stats_stream.sort_stats("cumtime").print_stats(15)

    print("\n" + "=" * 70)
    print("📊 RESULTADOS - PANDAS (Top 15 funciones por tiempo acumulado)")
    print("=" * 70)
    stats_pandas = pstats.Stats("profile_pandas.out")
    stats_pandas.sort_stats("cumtime").print_stats(15)

    # --- ARCHIVOS GENERADOS ---
    print("\n" + "=" * 70)
    print("✅ Archivos generados:")
    print("=" * 70)
    print("  📄 profile_streaming.out     - Resultados texto (streaming)")
    print("  📄 resultado_streaming.prof  - Para visualización gráfica")
    print("  📄 profile_pandas.out        - Resultados texto (pandas)")
    print("  📄 resultado_pandas.prof     - Para visualización gráfica")
    print("=" * 70)


def run_timeit(archivo="ventas.csv", num_registros=10000, repeticiones=5, chunksize=50000):
    """Ejecuta timeit para comparar rendimiento"""
    print("\n" + "=" * 70)
    print("BENCHMARK CON timeit")
    print("=" * 70)

    verificar_o_generar_datos(archivo, num_registros)

    print(f"\n📊 Configuración:")
    print(f"   • Registros: {num_registros:,}")
    print(f"   • Repeticiones: {repeticiones}")
    print(f"   • Chunksize (pandas): {chunksize:,}")
    print()

    # Setup común (sin generación de datos, ya existen)
    setup = f"""
from ventas import analizar_ventas_streaming, analizar_ventas_pandas
"""

    # --- STREAMING ---
    print("🌊 Midiendo Streaming...")
    stmt_streaming = f"analizar_ventas_streaming('{archivo}')"
    t_streaming = timeit.timeit(stmt=stmt_streaming, setup=setup, number=repeticiones)
    promedio_streaming = t_streaming / repeticiones

    print(f"   ✓ Tiempo total: {t_streaming:.4f}s")
    print(f"   ✓ Promedio: {promedio_streaming:.6f}s por ejecución")

    # --- PANDAS ---
    print(f"\n📦 Midiendo Pandas (chunksize={chunksize:,})...")
    stmt_pandas = f"analizar_ventas_pandas('{archivo}', chunksize={chunksize})"
    t_pandas = timeit.timeit(stmt=stmt_pandas, setup=setup, number=repeticiones)
    promedio_pandas = t_pandas / repeticiones

    print(f"   ✓ Tiempo total: {t_pandas:.4f}s")
    print(f"   ✓ Promedio: {promedio_pandas:.6f}s por ejecución")

    # --- COMPARACIÓN ---
    print("\n" + "=" * 70)
    print("COMPARACIÓN DE RENDIMIENTO")
    print("=" * 70)

    diferencia_ms = abs(promedio_streaming - promedio_pandas) * 1000

    print(f"\n{'Estrategia':<20} {'Tiempo Promedio':<20} {'Velocidad Relativa'}")
    print("-" * 70)

    if promedio_streaming < promedio_pandas:
        factor = promedio_pandas / promedio_streaming
        print(f"{'🌊 Streaming':<20} {promedio_streaming:.6f}s        ✅ Ganador ({factor:.2f}x más rápido)")
        print(f"{'📦 Pandas':<20} {promedio_pandas:.6f}s        {factor:.2f}x más lento")
    else:
        factor = promedio_streaming / promedio_pandas
        print(f"{'🌊 Streaming':<20} {promedio_streaming:.6f}s        {factor:.2f}x más lento")
        print(f"{'📦 Pandas':<20} {promedio_pandas:.6f}s        ✅ Ganador ({factor:.2f}x más rápido)")

    print(f"\n📏 Diferencia absoluta: {diferencia_ms:.2f}ms")


def run_all(archivo="ventas.csv", num_registros=10000, repeticiones=5, chunksize_timeit=50000, chunksize_cprofile=5000):
    """Ejecuta todas las herramientas de profiling"""
    # 1. Generar datos
    verificar_o_generar_datos(archivo, num_registros)

    # 2. cProfile
    run_cprofile(archivo, chunksize=chunksize_cprofile)

    # 3. timeit
    run_timeit(archivo, num_registros, repeticiones, chunksize=chunksize_timeit)

    # Resumen final
    print("=" * 70)
    print("\n📁 Archivos generados:")
    print("   • profile_streaming.out")
    print("   • profile_pandas.out")
    print("   • resultado_streaming.prof")
    print("   • resultado_pandas.prof")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Suite de herramientas de profiling para ventas.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python profiling.py --cprofile                    # Solo cProfile
  python profiling.py --timeit                      # Solo timeit
  python profiling.py --timeit --n 50000 --reps 10  # timeit con 50K registros
  python profiling.py --all                         # Ejecutar todo
  python profiling.py --all --n 100000              # Todo con 100K registros

Herramientas adicionales (ejecutar por separado):
  python -m memory_profiler ventas.py analizar ventas.csv
  kernprof -l -v ventas.py analizar ventas.csv
  snakeviz resultado_streaming.prof
        """
    )

    # Argumentos principales
    parser.add_argument("--cprofile", action="store_true",
                        help="Ejecutar cProfile (análisis de tiempo por función)")
    parser.add_argument("--timeit", action="store_true",
                        help="Ejecutar timeit (micro-benchmark)")
    parser.add_argument("--all", action="store_true",
                        help="Ejecutar todas las herramientas")

    # Parámetros de configuración
    parser.add_argument("--archivo", type=str, default="ventas.csv",
                        help="Nombre del archivo CSV (default: ventas.csv)")
    parser.add_argument("--n", type=int, default=10000,
                        help="Número de registros a generar (default: 10000)")
    parser.add_argument("--reps", type=int, default=5,
                        help="Número de repeticiones para timeit (default: 5)")
    parser.add_argument("--chunksize-timeit", type=int, default=50000,
                        help="Chunk size para pandas en timeit (default: 50000)")
    parser.add_argument("--chunksize-cprofile", type=int, default=5000,
                        help="Chunk size para pandas en cProfile (default: 5000)")

    args = parser.parse_args()

    # Si no se especifica nada, mostrar ayuda
    if not (args.cprofile or args.timeit or args.all):
        parser.print_help()
        return

    # Ejecutar herramientas solicitadas
    if args.all:
        run_all(
            archivo=args.archivo,
            num_registros=args.n,
            repeticiones=args.reps,
            chunksize_timeit=args.chunksize_timeit,
            chunksize_cprofile=args.chunksize_cprofile
        )
    else:
        if args.cprofile:
            run_cprofile(
                archivo=args.archivo,
                chunksize=args.chunksize_cprofile
            )

        if args.timeit:
            run_timeit(
                archivo=args.archivo,
                num_registros=args.n,
                repeticiones=args.reps,
                chunksize=args.chunksize_timeit
            )


if __name__ == "__main__":
    main()