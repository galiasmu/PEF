# 📊 Proyecto: Procesamiento de Datos de Ventas

> Sistema optimizado para generación, análisis y profiling de datos de ventas en archivos CSV

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Pytest-orange.svg)](https://pytest.org/)

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#-arquitectura)
- [Profiling](#-profiling-y-optimización)
- [Testing](#-testing)
- [Resultados](#-resultados)
- [Contribución](#-contribución)

## 🎯 Descripción

Este proyecto implementa un sistema completo de procesamiento de datos de ventas que cumple con los siguientes objetivos:

- ✅ Generación de archivos CSV sintéticos con datos de ventas
- ✅ Análisis eficiente de grandes volúmenes de datos (10,000+ registros)
- ✅ Dos estrategias de procesamiento optimizadas: **Streaming** y **Batching**
- ✅ Métricas de negocio: ventas totales, promedios, productos más vendidos
- ✅ Profiling completo con múltiples herramientas
- ✅ Suite de tests unitarios con pytest
- ✅ Código refactorizado siguiendo PEP8

## ✨ Características

### 🚀 Optimizaciones Implementadas

- **Eliminación de redundancia**: Funciones reutilizables y dataclasses
- **Batching**: Procesamiento por bloques configurable (50,000 registros por defecto)
- **Streaming**: Procesamiento iterativo con memoria constante O(1)
- **Type hints**: Código fuertemente tipado para mejor mantenibilidad
- **Generadores**: Uso eficiente de memoria para lectura de archivos

### 📈 Métricas Calculadas

| Métrica | Descripción |
|---------|-------------|
| **Ventas Totales** | Suma de `precio × cantidad` de todas las transacciones |
| **Promedio por Venta** | Valor promedio de cada transacción |
| **Producto Más Vendido** | Producto con mayor cantidad de unidades vendidas |
| **Cantidad Total** | Unidades totales del producto top |
| **Número de Registros** | Total de transacciones procesadas |

## 📦 Requisitos

### Requisitos Mínimos

- Python 3.8 o superior
- Sistema operativo: Windows, Linux o macOS

### Dependencias Obligatorias

```
# Ninguna para funcionalidad básica (solo stdlib)
```

### Dependencias Opcionales

```
pandas>=1.5.0          # Para análisis con batching
pytest>=7.0.0          # Para ejecutar tests
memory_profiler>=0.60  # Para análisis de memoria
line_profiler>=4.0     # Para profiling línea por línea
snakeviz>=2.1.0        # Para visualización de cProfile
```

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/procesamiento-ventas.git
cd procesamiento-ventas
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
# Instalación mínima (solo streaming)
pip install -r requirements-minimal.txt

# Instalación completa (con todas las herramientas)
pip install -r requirements.txt
```

### Contenido de `requirements.txt`

```txt
pandas>=1.5.0
pytest>=7.0.0
memory_profiler>=0.60
line_profiler>=4.0
snakeviz>=2.1.0
```

## 🚀 Uso

### Interfaz de Línea de Comandos

#### Generar archivo CSV de ventas

```bash
# Generar 10,000 registros (por defecto)
python ventas.py generar ventas.csv

# Generar cantidad personalizada
python ventas.py generar ventas.csv --n 100000 --seed 42
```

#### Analizar datos con Streaming

```bash
python ventas.py analizar ventas.csv --modo stream
```

**Salida esperada:**
```
--- 📊 Resultados del Análisis de Ventas ---
Registros: 10,000
Ventas Totales: $4,357,892.50
Promedio por Venta: $435.79
Producto Más Vendido: 'Laptop' con 5,432 unidades.
-------------------------------------------
```

#### Analizar datos con Pandas (Batching)

```bash
python ventas.py analizar ventas.csv --modo pandas --chunksize 50000
```

### Uso Programático

```python
from ventas import generar_csv_ventas, analizar_ventas_streaming, VentasMetrics

# Generar datos
generar_csv_ventas("ventas.csv", num_registros=10000, seed=42)

# Analizar
metrics: VentasMetrics = analizar_ventas_streaming("ventas.csv")

print(f"Ventas totales: ${metrics.ventas_totales:,.2f}")
print(f"Producto top: {metrics.producto_mas_vendido}")
```

## 🏗️ Arquitectura

### Estructura de Archivos

```
Parcial2-PEF/
│
├── ventas.py               # Módulo principal
├── profiling.py            # Scripts de profiling
├── requirements.txt        # Dependencias
├── README.md               # Este archivo
├── tests/
│   └── test_ventas.py      # Tests unitarios│
│
├── ventas.csv              # Archivo de datos (generado)
├── profile.out             # Resultados de cProfile (generado)
└── ventas.py.lprof         # Resultados de line_profiler (generado)
```

### Componentes Principales

#### `ventas.py`

**Funciones principales:**

| Función | Descripción | Complejidad |
|---------|-------------|-------------|
| `generar_csv_ventas()` | Genera CSV sintético | O(n) |
| `analizar_ventas_streaming()` | Análisis con streaming | O(n), Memoria: O(1) |
| `analizar_ventas_pandas()` | Análisis con batching | O(n), Memoria: O(chunk) |
| `_iter_csv_filas()` | Generador para lectura | O(1) por elemento |

**Clase de datos:**

```python
@dataclass
class VentasMetrics:
    ventas_totales: float
    promedio_por_venta: float
    producto_mas_vendido: str
    cantidad_mas_vendida: int
    num_registros: int
```

#### `test_ventas.py`

Tests implementados:
- ✅ `test_generar_csv()` - Validación de generación
- ✅ `test_iterador_tipos()` - Verificación de tipos
- ✅ `test_analizar_streaming()` - Test de streaming
- ✅ `test_analizar_pandas()` - Test de batching

#### `profiling.py`

Scripts auxiliares para medición de rendimiento con `timeit`.

## 🔍 Profiling y Optimización

### 1. cProfile - Análisis de Tiempo por Función

```bash
# Generar perfil
python -m cProfile -o profile.out ventas.py analizar ventas.csv

# Ver resultados (top 20 funciones)
python -c "import pstats; p=pstats.Stats('profile.out'); p.sort_stats('cumtime').print_stats(20)"

# Visualización interactiva
pip install snakeviz
snakeviz profile.out
```

### 2. line_profiler - Análisis Línea por Línea

```bash
# Ejecutar profiling (con decorador @profile en las funciones)
kernprof -l -v ventas.py analizar ventas.csv

# Ver resultados guardados
python -m line_profiler ventas.py.lprof
```

**Nota:** Asegúrate de que las funciones tengan el decorador `@profile`:

```python
@profile
def analizar_ventas_streaming(nombre_archivo: str) -> VentasMetrics:
    # ...
```

### 3. memory_profiler - Análisis de Memoria

```bash
# Instalar
pip install memory_profiler

# Ejecutar
python -m memory_profiler ventas.py analizar ventas.csv
```

**Salida esperada:**
```
Line #    Mem usage    Increment   Line Contents
================================================
    45     50.2 MiB     50.2 MiB   @profile
    46                             def analizar_ventas_streaming(nombre_archivo: str):
    47     50.2 MiB      0.0 MiB       cantidades_por_producto = {}
    48     50.2 MiB      0.0 MiB       suma_ventas = 0.0
    ...
```

### 4. timeit - Micro-benchmarks

```bash
# Usar script auxiliar
python profiling.py --timeit
```

**Salida esperada:**
```
[timeit] 5 ejecuciones -> 2.3456s total; 0.469120s por run
```

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest test_ventas.py -v
```

### Ejecutar tests específicos

```bash
# Solo test de streaming
pytest test_ventas.py::test_analizar_streaming -v

# Solo tests de generación
pytest test_ventas.py::test_generar_csv -v
```

### Cobertura de código

```bash
pip install pytest-cov
pytest test_ventas.py --cov=ventas --cov-report=html
```

Abre `htmlcov/index.html` para ver el reporte visual.

### Salida esperada

```
========================= test session starts =========================
test_ventas.py::test_generar_csv PASSED                         [ 25%]
test_ventas.py::test_iterador_tipos PASSED                      [ 50%]
test_ventas.py::test_analizar_streaming PASSED                  [ 75%]
test_ventas.py::test_analizar_pandas PASSED                     [100%]

========================= 4 passed in 2.34s =========================
```

## 📊 Resultados

### Comparación de Estrategias

| Métrica | Streaming | Pandas (Batching) |
|---------|-----------|-------------------|
| **Memoria** | ~50 MB (constante) | ~200 MB (variable según chunk) |
| **Velocidad (10K)** | ~0.05s | ~0.08s |
| **Velocidad (1M)** | ~5.2s | ~4.8s |
| **Dependencias** | Ninguna | Pandas + NumPy |
| **Escalabilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Recomendaciones

- **Usa Streaming cuando:**
  - Trabajas con archivos muy grandes (>1GB)
  - Necesitas memoria constante
  - No tienes pandas instalado
  - Priorizas simplicidad

- **Usa Pandas cuando:**
  - Necesitas operaciones complejas
  - Trabajas con múltiples agregaciones
  - Tienes memoria suficiente
  - Priorizas velocidad en operaciones vectorizadas

## 🎓 Aprendizajes Clave

### Optimizaciones Implementadas

1. **Eliminación de Redundancia**
   - Funciones auxiliares reutilizables
   - Dataclasses para estructuras de datos
   - Generadores para iteración eficiente

2. **Batching (Chunking)**
   - Parámetro `chunksize` configurable
   - Procesamiento incremental
   - Memoria controlada

3. **Streaming**
   - Lectura línea por línea
   - Sin cargar todo el archivo
   - Memoria O(1)

4. **Type Hints**
   - Código más mantenible
   - Mejor autocompletado en IDEs
   - Detección temprana de errores

## 📝 Estándares de Código

Este proyecto sigue:

- ✅ **PEP 8** - Guía de estilo de Python
- ✅ **PEP 257** - Docstring conventions
- ✅ **Type hints** - PEP 484
- ✅ **Dataclasses** - PEP 557

### Verificar estilo

```bash
# Instalar herramientas
pip install flake8 black

# Verificar PEP8
flake8 ventas.py

# Formatear automáticamente
black ventas.py
```