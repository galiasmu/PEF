# Proyecto 1 – Procesamiento de Datos de Ventas

Este repositorio contiene una solución **refactorizada**, con **batching**, **medición de rendimiento** y **tests**.

## Estructura
```
proyecto_ventas/
├── ventas.py         # Módulo principal: generación + análisis (stream y pandas)
├── profiling.py      # Ayudas para cProfile, line_profiler, memory_profiler y timeit
└── tests/
    └── test_ventas.py
```

## Requisitos

- Python 3.10+
- Paquetes opcionales:
  - `pandas` (para el modo por chunks con DataFrames)
  - `line_profiler` (herramienta de profiling por línea: `kernprof`)
  - `memory_profiler` (para medir memoria)
  - `pytest` (tests)

Instalación sugerida:
```bash
pip install -U pandas line_profiler memory_profiler pytest
```

## Uso

### 1) Generar CSV de 10.000 filas
```bash
python ventas.py generar ventas.csv --n 10000 --seed 42
```

### 2) Analizar (streaming, sin cargar todo a memoria)
```bash
python ventas.py analizar ventas.csv --modo stream
```

### 3) Analizar (pandas con chunks)
```bash
python ventas.py analizar ventas.csv --modo pandas --chunksize 5000
```

## Optimización aplicada

- **Código redundante eliminado** y funciones reutilizables (`_iter_csv_filas`, `VentasMetrics`).
- **Batching / streaming**:
  - Implementación manual leyendo fila por fila con `csv.DictReader` (bajo uso de memoria).
  - Opción `pandas.read_csv(..., chunksize=N)` para procesar por bloques.
- **Cálculo de métricas en una sola pasada**: suma de ventas, conteo y agregación de cantidades por producto.
- **Salida tipada** mediante `@dataclass` para claridad y tests.

## Medición de rendimiento

### cProfile
```bash
python -m cProfile -o profile.out ventas.py analizar ventas.csv
python - <<'PY'
import pstats
p = pstats.Stats("profile.out")
p.sort_stats("cumtime").print_stats(20)
PY
```

### line_profiler
Marca funciones con `# @profile` (ya está comentado en el código) y corre:
```bash
kernprof -l -v ventas.py analizar ventas.csv
```

### memory_profiler
Usa el *decorator* especial `@profile` (comentado) o `-m memory_profiler`:
```bash
python -m memory_profiler ventas.py analizar ventas.csv
```

### timeit (micro-benchmark)
```bash
python profiling.py --timeit
```

## Tests unitarios

Ejecuta:
```bash
pytest -q
```

Cubre:
- Generación de CSV y cabeceras
- Tipos de columnas desde el iterador
- Métricas en modo streaming
- (si `pandas` está instalado) métricas con chunks

## Notas

- El promedio de venta se calcula como **suma(Venta_Total)/n_registros**.
- Para **datos reales grandes**, prefiere `--modo stream` por menor consumo de memoria.
- El análisis es determinista usando `--seed`, lo cual facilita repetir resultados para profiling.
