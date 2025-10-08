# tests/test_ventas.py
import os
import csv
import math
import pytest

from ventas import (
    generar_csv_ventas,
    analizar_ventas_streaming,
    analizar_ventas_pandas,
    VentasMetrics,
    _iter_csv_filas,
)

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def test_generar_csv(tmp_path):
    ruta = tmp_path / "ventas.csv"
    generar_csv_ventas(str(ruta), num_registros=100, seed=123)
    assert ruta.exists()
    # revisa cabeceras
    with open(ruta, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ['ID_Venta', 'Producto', 'Precio_Unitario', 'Cantidad']
        filas = list(reader)
        assert len(filas) == 100


def test_iterador_tipos(tmp_path):
    ruta = tmp_path / "ventas.csv"
    generar_csv_ventas(str(ruta), num_registros=3, seed=1)
    filas = list(_iter_csv_filas(str(ruta)))
    assert len(filas) == 3
    id1, prod1, precio1, cant1 = filas[0]
    assert isinstance(id1, int)
    assert isinstance(prod1, str)
    assert isinstance(precio1, float)
    assert isinstance(cant1, int)


def test_analizar_streaming(tmp_path):
    ruta = tmp_path / "ventas.csv"
    generar_csv_ventas(str(ruta), num_registros=1000, seed=7)
    m = analizar_ventas_streaming(str(ruta))
    assert isinstance(m, VentasMetrics)
    assert m.num_registros == 1000
    assert m.ventas_totales > 0
    assert m.promedio_por_venta > 0
    assert m.cantidad_mas_vendida >= 1
    assert isinstance(m.producto_mas_vendido, str)


@pytest.mark.skipif("pandas" not in globals(), reason="pandas no disponible")
def test_analizar_pandas(tmp_path):
    ruta = tmp_path / "ventas.csv"
    generar_csv_ventas(str(ruta), num_registros=1000, seed=7)
    m = analizar_ventas_pandas(str(ruta), chunksize=200)
    assert m.num_registros == 1000
    assert m.ventas_totales > 0
