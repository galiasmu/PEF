"""
Bloque de medición de rendimiento con cProfile.
Forma parte de la consigna: “Medir rendimiento con cProfile y line_profiler”.
"""

import cProfile
import pstats
from ventas import generar_csv_ventas, analizar_ventas_streaming, analizar_ventas_pandas

def medir_con_cprofile():
    """
    Ejecuta análisis de ventas con cProfile y muestra las 20 funciones más lentas.
    """

    archivo = "ventas.csv"

    # --- 1️⃣ Generar archivo si no existe ---
    try:
        open(archivo)
        print(f"✅ Archivo '{archivo}' encontrado, se reutiliza.")
    except FileNotFoundError:
        print(f"⚙️ Generando archivo '{archivo}' con 10.000 registros para pruebas...")
        generar_csv_ventas(archivo, 10000)

    # --- 2️⃣ Ejecutar el perfilado con cProfile ---
    print("\n🚀 Ejecutando análisis con cProfile (modo STREAMING)...")
    cProfile.run("analizar_ventas_streaming('ventas.csv')", "profile_streaming.out")

    print("\n🚀 Ejecutando análisis con cProfile (modo PANDAS por chunks)...")
    cProfile.run("analizar_ventas_pandas('ventas.csv', chunksize=5000)", "profile_pandas.out")

    # --- 3️⃣ Mostrar resultados resumidos ---
    print("\n--- 📊 Resultados de cProfile (modo STREAMING) ---")
    stats_stream = pstats.Stats("profile_streaming.out")
    stats_stream.sort_stats("cumtime").print_stats(15)

    print("\n--- 📊 Resultados de cProfile (modo PANDAS) ---")
    stats_pandas = pstats.Stats("profile_pandas.out")
    stats_pandas.sort_stats("cumtime").print_stats(15)


if __name__ == "__main__":
    medir_con_cprofile()
