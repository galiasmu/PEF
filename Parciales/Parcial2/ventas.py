#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ventas.py
---------
Proyecto 1 – Procesamiento de Datos de Ventas.
"""
import csv
import random
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, Optional

try:
    import pandas as _pd  # opcional
except Exception:
    _pd = None


PRODUCTOS_PREDETERMINADOS = [
    "Laptop", "Mouse", "Teclado", "Monitor", "Webcam",
    "Micrófono", "Silla Gamer", "Auriculares", "Impresora", "Router WiFi",
]


@dataclass
class VentasMetrics:
    ventas_totales: float
    promedio_por_venta: float
    producto_mas_vendido: str
    cantidad_mas_vendida: int
    num_registros: int


def generar_csv_ventas(nombre_archivo: str = "ventas.csv", num_registros: int = 10_000,
                       productos: Optional[Iterable[str]] = None,
                       seed: Optional[int] = 42) -> str:
    if productos is None:
        productos = PRODUCTOS_PREDETERMINADOS

    if seed is not None:
        random.seed(seed)

    cabeceras = ["ID_Venta", "Producto", "Precio_Unitario", "Cantidad"]

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cabeceras)
        for i in range(1, num_registros + 1):
            producto = random.choice(list(productos))
            precio = round(random.uniform(20.50, 850.99), 2)
            cantidad = random.randint(1, 10)
            writer.writerow([i, producto, precio, cantidad])

    return nombre_archivo


def _iter_csv_filas(nombre_archivo: str) -> Iterable[Tuple[int, str, float, int]]:
    with open(nombre_archivo, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (
                int(row["ID_Venta"]),
                row["Producto"],
                float(row["Precio_Unitario"]),
                int(row["Cantidad"]),
            )


def analizar_ventas_streaming(nombre_archivo: str) -> VentasMetrics:
    cantidades_por_producto: Dict[str, int] = {}
    suma_ventas = 0.0
    n = 0

    # @profile  # descomenta para memory_profiler/line_profiler
    for (_id, producto, precio, cantidad) in _iter_csv_filas(nombre_archivo):
        total = precio * cantidad
        suma_ventas += total
        n += 1
        cantidades_por_producto[producto] = cantidades_por_producto.get(producto, 0) + cantidad

    if n == 0:
        return VentasMetrics(0.0, 0.0, "", 0, 0)

    producto_top, cant_top = max(cantidades_por_producto.items(), key=lambda kv: kv[1])
    promedio = suma_ventas / n

    return VentasMetrics(
        ventas_totales=round(suma_ventas, 2),
        promedio_por_venta=round(promedio, 2),
        producto_mas_vendido=producto_top,
        cantidad_mas_vendida=int(cant_top),
        num_registros=n,
    )


def analizar_ventas_pandas(nombre_archivo: str, chunksize: int = 50_000) -> VentasMetrics:
    if _pd is None:
        raise RuntimeError("pandas no está disponible en el entorno.")

    suma_ventas = 0.0
    n = 0
    cantidades_por_producto: Dict[str, int] = {}

    # @profile
    for chunk in _pd.read_csv(nombre_archivo, chunksize=chunksize):
        chunk["Venta_Total"] = chunk["Precio_Unitario"] * chunk["Cantidad"]
        suma_ventas += float(chunk["Venta_Total"].sum())
        n += int(len(chunk))
        cantidades_chunk = chunk.groupby("Producto")["Cantidad"].sum().to_dict()
        for prod, cnt in cantidades_chunk.items():
            cantidades_por_producto[prod] = cantidades_por_producto.get(prod, 0) + int(cnt)

    if n == 0:
        return VentasMetrics(0.0, 0.0, "", 0, 0)

    producto_top, cant_top = max(cantidades_por_producto.items(), key=lambda kv: kv[1])
    promedio = suma_ventas / n

    return VentasMetrics(
        ventas_totales=round(suma_ventas, 2),
        promedio_por_venta=round(promedio, 2),
        producto_mas_vendido=producto_top,
        cantidad_mas_vendida=int(cant_top),
        num_registros=n,
    )


def _imprimir_resultados(m: VentasMetrics) -> None:
    print("\n--- 📊 Resultados del Análisis de Ventas ---")
    print(f"Registros: {m.num_registros:,}")
    print(f"Ventas Totales: ${m.ventas_totales:,.2f}")
    print(f"Promedio por Venta: ${m.promedio_por_venta:,.2f}")
    if m.producto_mas_vendido:
        print(f"Producto Más Vendido: '{m.producto_mas_vendido}' con {m.cantidad_mas_vendida} unidades.")
    print("-------------------------------------------\n")


def _parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Proyecto 1 – Procesamiento de Datos de Ventas")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generar", help="Genera un CSV sintético de ventas")
    p_gen.add_argument("archivo", nargs="?", default="ventas.csv")
    p_gen.add_argument("--n", type=int, default=10_000, help="número de registros")
    p_gen.add_argument("--seed", type=int, default=42, help="semilla aleatoria")

    p_ana = sub.add_parser("analizar", help="Analiza un CSV (streaming por defecto)")
    p_ana.add_argument("archivo")
    p_ana.add_argument("--modo", choices=["stream", "pandas"], default="stream", help="método de análisis")
    p_ana.add_argument("--chunksize", type=int, default=50_000, help="tamaño de chunk para pandas")

    return p.parse_args()


def main():
    args = _parse_args()
    if args.cmd == "generar":
        ruta = generar_csv_ventas(args.archivo, args.n, seed=args.seed)
        print(f"✅ Archivo '{ruta}' con {args.n:,} registros generado.")
    elif args.cmd == "analizar":
        if args.modo == "stream":
            metrics = analizar_ventas_streaming(args.archivo)
        else:
            metrics = analizar_ventas_pandas(args.archivo, chunksize=args.chunksize)
        _imprimir_resultados(metrics)


if __name__ == "__main__":
    main()
