#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ventas.py
---------
Proyecto 1 – Procesamiento de Datos de Ventas.

Este módulo implementa un sistema completo de generación y análisis de datos
de ventas desde archivos CSV. Proporciona dos estrategias de procesamiento
optimizadas: streaming (línea por línea) y batching con pandas (por bloques).

Módulos principales:
    - generar_csv_ventas: Genera archivos CSV sintéticos con datos aleatorios
    - analizar_ventas_streaming: Análisis eficiente con memoria constante O(1)
    - analizar_ventas_pandas: Análisis por bloques con operaciones vectorizadas

Fecha: Octubre 2025
"""
import csv
import random
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple, Optional

# Usar:
try:
    from memory_profiler import profile
except ImportError:
    def profile(func):
        return func

try:
    import pandas as _pd
except Exception:
    _pd = None


PRODUCTOS_PREDETERMINADOS = [
    "Laptop", "Mouse", "Teclado", "Monitor", "Webcam",
    "Micrófono", "Silla Gamer", "Auriculares", "Impresora", "Router WiFi",
]


@dataclass
class VentasMetrics:
    """
       Dataclass que encapsula las métricas calculadas del análisis de ventas.

       Attributes:
           ventas_totales (float): Suma total de todas las ventas (precio × cantidad)
           promedio_por_venta (float): Valor promedio de cada transacción
           producto_mas_vendido (str): Nombre del producto con más unidades vendidas
           cantidad_mas_vendida (int): Número de unidades del producto más vendido
           num_registros (int): Cantidad total de registros procesados
       """
    ventas_totales: float
    promedio_por_venta: float
    producto_mas_vendido: str
    cantidad_mas_vendida: int
    num_registros: int


def generar_csv_ventas(nombre_archivo: str = "ventas.csv", num_registros: int = 10_000,
                       productos: Optional[Iterable[str]] = None,
                       seed: Optional[int] = 42) -> str:
    """
    Genera un archivo CSV con datos sintéticos de ventas.

    Crea un archivo CSV con registros aleatorios de ventas que incluyen
    ID, producto, precio unitario y cantidad. Los datos son reproducibles
    si se especifica una semilla.

    Args:
        nombre_archivo (str): Ruta del archivo CSV a crear.
            Default: "ventas.csv"
        num_registros (int): Cantidad de registros a generar.
            Default: 10,000
        productos (Optional[Iterable[str]]): Lista de nombres de productos.
            Si es None, usa PRODUCTOS_PREDETERMINADOS.
        seed (Optional[int]): Semilla para generación aleatoria reproducible.
            Si es None, los datos serán diferentes en cada ejecución.
            Default: 42

    Returns:
        str: Ruta del archivo generado (mismo que nombre_archivo)

    Note:
        El archivo generado tiene las siguientes columnas:
        - ID_Venta: Entero secuencial (1 a num_registros)
        - Producto: Nombre del producto (string)
        - Precio_Unitario: Float entre 20.50 y 850.99
        - Cantidad: Entero entre 1 y 10
    """
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
    """
    Generador que lee un CSV línea por línea con conversión automática de tipos.

    Esta función auxiliar implementa un generador que lee el archivo CSV
    de forma iterativa (streaming), convirtiendo cada campo al tipo apropiado.
    Esto permite procesar archivos grandes sin cargarlos completamente en memoria.

    Args:
        nombre_archivo (str): Ruta del archivo CSV a leer

    Yields:
        Tuple[int, str, float, int]: Tupla con (ID_Venta, Producto,
            Precio_Unitario, Cantidad) con tipos convertidos

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si los datos no pueden convertirse a los tipos esperados
        KeyError: Si faltan columnas requeridas en el CSV
    """
    with open(nombre_archivo, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (
                int(row["ID_Venta"]),
                row["Producto"],
                float(row["Precio_Unitario"]),
                int(row["Cantidad"]),
            )

@profile
def analizar_ventas_streaming(nombre_archivo: str) -> VentasMetrics:
    """
    Analiza ventas usando estrategia de streaming (línea por línea).

    Procesa el archivo CSV de forma iterativa sin cargar todo el contenido
    en memoria. Esta estrategia tiene complejidad temporal O(n) y complejidad
    espacial O(1) respecto al tamaño del archivo, usando solo memoria para
    contadores y agregaciones.

    Args:
        nombre_archivo (str): Ruta del archivo CSV a analizar

    Returns:
        VentasMetrics: Objeto con todas las métricas calculadas

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el CSV tiene formato inválido

    Note:
        Ventajas de esta estrategia:
        - Memoria constante (~50 MB) sin importar tamaño del archivo
        - Puede procesar archivos de 1 GB, 10 GB o más
        - Sin dependencias externas (solo biblioteca estándar)

        Desventajas:
        - Más lento que pandas para operaciones complejas
        - Operaciones no vectorizadas
    """
    cantidades_por_producto: Dict[str, int] = {}
    suma_ventas = 0.0
    n = 0

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

@profile
def analizar_ventas_pandas(nombre_archivo: str, chunksize: int = 50_000) -> VentasMetrics:
    """
    Analiza ventas usando estrategia de batching con pandas.

    Procesa el archivo CSV en bloques (chunks) del tamaño especificado,
    aprovechando las operaciones vectorizadas de NumPy para mejor rendimiento.
    La memoria usada es proporcional al chunksize, no al tamaño total del archivo.

    Args:
        nombre_archivo (str): Ruta del archivo CSV a analizar
        chunksize (int): Número de filas a procesar por bloque.
            Default: 50,000. Valores mayores usan más memoria pero pueden
            ser más rápidos. Valores menores usan menos memoria pero más
            iteraciones.

    Returns:
        VentasMetrics: Objeto con todas las métricas calculadas

    Raises:
        RuntimeError: Si pandas no está instalado
        FileNotFoundError: Si el archivo no existe
        pd.errors.ParserError: Si el CSV tiene formato inválido

    Note:
        Ventajas de esta estrategia:
        - Más rápido que streaming para operaciones complejas
        - Operaciones vectorizadas (NumPy en C)
        - Métodos built-in de pandas (groupby, pivot, merge)

        Desventajas:
        - Usa más memoria (proporcional al chunksize)
        - Requiere pandas + numpy instalados
        - Overhead de conversión a DataFrame

    Warning:
        Si chunksize es muy grande y el archivo es enorme, puede quedarse
        sin memoria. Ajusta chunksize según la RAM disponible.
    """
    if _pd is None:
        raise RuntimeError("pandas no está disponible en el entorno.")

    suma_ventas = 0.0
    n = 0
    cantidades_por_producto: Dict[str, int] = {}

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


def _imprimir_resultados(m: VentasMetrics) -> None: #pragma: no cover
    """
    Imprime los resultados del análisis en formato legible.

    Función auxiliar para mostrar las métricas calculadas en consola
    con formato amigable para el usuario.

    Args:
        m (VentasMetrics): Objeto con las métricas a imprimir
    """
    print("\n--- 📊 Resultados del Análisis de Ventas ---")
    print(f"Registros: {m.num_registros:,}")
    print(f"Ventas Totales: ${m.ventas_totales:,.2f}")
    print(f"Promedio por Venta: ${m.promedio_por_venta:,.2f}")
    if m.producto_mas_vendido:
        print(f"Producto Más Vendido: '{m.producto_mas_vendido}' con {m.cantidad_mas_vendida} unidades.")
    print("-------------------------------------------\n")


def _parse_args(): #pragma: no cover
    """
       Parsea los argumentos de línea de comandos.

       Configura el parser de argparse con dos subcomandos: generar y analizar.
       Esta función define la interfaz CLI del módulo.

       Returns:
           argparse.Namespace: Objeto con los argumentos parseados

       Note:
           Esta función está excluida de la cobertura de tests porque
           las funciones CLI se testean manualmente, no con unittest.
       """
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


def main(): #pragma: no cover
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