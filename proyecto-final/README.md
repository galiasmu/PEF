# Análisis en Tiempo Real de Redes Sociales

**Materia:** Programación Eficiente (PEF) — Universidad Blas Pascal
**Consigna:** Final PEF 2025, consigna 8 — *Sistema de Análisis en Tiempo Real de Redes Sociales*
**Autor:** Gali Asmuzi

---

## ¿Qué hace?

Recolecta los comentarios de un video (o canal) de YouTube y los analiza en tiempo casi real.
Cada cierto intervalo (una *ventana de tiempo*) calcula:

- **Cantidad de comentarios** recibidos en la ventana.
- **Hashtags más usados** (top 10) de la ventana.
- **Tendencias**: los hashtags más usados en el último minuto (`TREND_SECONDS`).
- **Sentimiento promedio** (positivo / neutral / negativo), usando un modelo de IA
  de procesamiento de lenguaje natural
  (`cardiffnlp/twitter-xlm-roberta-base-sentiment`, de Hugging Face `transformers`).

Los resultados se muestran en vivo en un **dashboard web**.

## Arquitectura

```
YouTube API (o fuente simulada)
      │   generador async: un lote de comentarios nuevos por consulta
      ▼
  productor ──► cola acotada ──► ventanas de tiempo
                                        │
                                        ▼
                        sentimiento por lote (en otro hilo)
                                        │
                                        ▼
                     resumen + tendencias (TTL) ──► WebSocket (broadcast)
                                                          │
                                                          ▼
                                            dashboard 1, dashboard 2, ...
```

El pipeline arranca **una sola vez**, junto con el servidor, y reparte (*broadcast*) cada resumen a
todos los clientes conectados: no importa cuántas pestañas del dashboard estén abiertas, se consulta
a YouTube y se usa el modelo una sola vez por ventana.

| Módulo | Responsabilidad |
|---|---|
| `app/sources.py` | Fuentes de datos: YouTube (`aiohttp`) y simulada. Son **generadores asíncronos** que entregan un lote de comentarios nuevos por consulta. |
| `app/pipeline.py` | **Productor** que pone los comentarios en una **cola acotada** y **ventanas de tiempo** que los agrupan. |
| `app/sentiment.py` | Análisis de sentimiento **por lote**, con **memoización**. Si el modelo no carga, avisa y usa un análisis léxico. |
| `app/cache.py` | Cache **LRU** en O(1) (`OrderedDict`). |
| `app/trends.py` | **Tendencias** con vencimiento por tiempo (TTL): `Counter` + `deque`. |
| `app/aggregator.py` | Resumen de cada ventana y extracción de hashtags (`Counter`). |
| `app/main.py` | Servidor: arranca el pipeline, corre el modelo en otro hilo y reparte los resúmenes por WebSocket. |
| `app/config.py` | Configuración, leída una sola vez desde el `.env`. |
| `ui-mini/` | Dashboard (HTML + Chart.js): últimas 30 ventanas, tendencias, reconexión automática. |

## Requisitos de la consigna y dónde están

| Requisito | Dónde y cómo |
|---|---|
| Concurrencia / paralelismo para procesar el stream | **Concurrencia** con `asyncio`: el productor corre como tarea aparte y sigue trayendo comentarios mientras se procesa la ventana anterior (`pipeline.py`). **Paralelismo**: el modelo corre en otro hilo con `asyncio.to_thread`; torch libera el GIL mientras calcula (`main.py`). |
| Batching de mensajes en ventanas temporales | `time_windows` agrupa los comentarios en ventanas de `WINDOW_SECONDS` y emite aunque estén vacías (`pipeline.py`). El modelo analiza cada ventana como un lote (`sentiment.py`). |
| Caching inteligente de tendencias recurrentes | `TrendingHashtags`: cada ventana suma sus hashtags y, pasado `TREND_SECONDS`, se descuenta sola; lo viejo se invalida automáticamente (`trends.py`). Además, `LRUCache` memoiza el sentimiento de textos repetidos (`cache.py`). |
| Generadores para recorrer el stream sin cargar todo | Las fuentes y las ventanas son generadores asíncronos (`sources.py`, `pipeline.py`). |
| Conteo eficiente de hashtags | `collections.Counter` y `most_common` (`aggregator.py`, `trends.py`). |
| Profiling y refactorización | cProfile y benchmarks de antes y después (`backend/scripts/`, resultados en [docs/rendimiento.md](docs/rendimiento.md)). Código refactorizado en módulos con una sola responsabilidad, PEP 8 verificado con `flake8`. |
| Testing para validar el análisis | 23 tests con pytest (93 % de cobertura): unitarios, integración de punta a punta, Hypothesis y doctest. |
| IA: análisis de sentimiento con ML/NLP | Modelo transformer multilingüe de Hugging Face (`sentiment.py`). |

## Decisiones de optimización

Cada optimización se midió contra la versión anterior (detalle en [docs/rendimiento.md](docs/rendimiento.md)):

| Decisión | Por qué | Resultado medido |
|---|---|---|
| Sentimiento **por lote** | Llamar al modelo una vez por ventana en lugar de una vez por comentario. | 3x más rápido |
| **Memoización** con cache LRU | Los comentarios repetidos (spam, copias) no vuelven a pasar por el modelo. | De 549 ms a 0,03 ms |
| Modelo **en otro hilo** | Mientras el modelo analiza, el servidor sigue atendiendo. | Pausa máxima del servidor: de 543 ms a 17 ms |
| `LRUCache` con `OrderedDict` | El cache original buscaba el más viejo recorriendo todo (O(n)); ahora es O(1). | 266x más rápido |
| `SeenIds` (`set` + `deque`) | El `set` original de comentarios vistos crecía sin límite. | 15x menos memoria |
| Tendencias **incrementales** | Solo se suma la ventana nueva y se descuentan las vencidas, en vez de recalcular todo. | 2x con 1 hora de datos, y la diferencia crece con el tiempo |
| **Un solo pipeline** con broadcast | Antes cada pestaña del dashboard hacía sus propias consultas a YouTube y su propio análisis. | N pestañas → 1 consulta por ventana |
| `aiohttp` en lugar de `requests` | `requests` bloqueaba todo el servidor mientras esperaba la red. | El servidor no se frena esperando a YouTube |

**Dónde se va el tiempo (cProfile):** el modelo de IA se lleva el **99,9 %** del procesamiento, y el
conteo de hashtags y las tendencias, menos del 0,1 %. Por eso las optimizaciones se concentraron en
el modelo: se midió primero y se optimizó el cuello de botella, en lugar de optimizar de forma
prematura lo que ya era rápido.

## Estructura

```
proyecto-final/
├── backend/
│   ├── app/
│   │   ├── main.py        # servidor FastAPI: arranca el pipeline y reparte los resúmenes
│   │   ├── config.py      # configuración (lee el .env)
│   │   ├── sources.py     # fuentes de datos: YouTube y simulada (generadores async)
│   │   ├── pipeline.py    # productor, cola y ventanas de tiempo
│   │   ├── sentiment.py   # análisis de sentimiento por lote, con memoización
│   │   ├── cache.py       # cache LRU
│   │   ├── trends.py      # tendencias con vencimiento (TTL)
│   │   ├── aggregator.py  # resumen de cada ventana y extracción de hashtags
│   │   └── tests/         # tests con pytest
│   ├── scripts/           # benchmarks y profiling
│   ├── requirements.txt
│   └── .env.example       # plantilla de configuración
├── docs/
│   └── rendimiento.md     # mediciones de antes y después
└── ui-mini/               # dashboard web (HTML + Chart.js)
```

## Cómo correrlo

### Requisitos

- Python 3.12
- Una API key de **YouTube Data API v3** ([cómo obtenerla](https://developers.google.com/youtube/v3/getting-started)).
  No hace falta si se usa la fuente simulada (`SOURCE=simulated`).

### Instalación

```bash
cd proyecto-final/backend
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

En Linux/Mac: `python3 -m venv .venv` y `.venv/bin/python -m pip install -r requirements.txt`.

Los comandos de abajo usan `python` como si el entorno estuviera activado
(`.venv\Scripts\activate`). Si PowerShell no deja activarlo, se puede reemplazar `python` por
`.venv\Scripts\python` en cada comando.

### Configuración

Copiar la plantilla `backend/.env.example` como `backend/.env` y completar los valores.
El `.env` no se sube al repositorio.

```bash
copy .env.example .env
```

En Linux/Mac: `cp .env.example .env`.

| Variable | Default | Descripción |
|---|---|---|
| `SOURCE` | `youtube` | `youtube` (comentarios reales) o `simulated` (comentarios falsos, sin API key) |
| `YOUTUBE_API_KEY` | — | Clave de la API de YouTube (obligatoria con `SOURCE=youtube`) |
| `TARGET_TYPE` | `video` | `video` o `channel` |
| `TARGET_ID` | — | ID del video (lo que sigue a `watch?v=` en la URL) o del canal |
| `POLL_INTERVAL` | `5` | Segundos entre consultas a YouTube |
| `WINDOW_SECONDS` | `10` | Duración de cada ventana de análisis, en segundos |
| `TREND_SECONDS` | `60` | Las tendencias cuentan los hashtags de los últimos N segundos |
| `MAX_QUEUE` | `5000` | Tamaño máximo de la cola interna |
| `SENTIMENT_MODEL` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Modelo de Hugging Face para el sentimiento |

Cuota de YouTube: cada consulta gasta 1 unidad y el límite gratuito es de 10.000 por día. Con
`POLL_INTERVAL=5`, el servidor prendido todo el día haría 17.280 consultas; para dejarlo corriendo
muchas horas conviene usar `POLL_INTERVAL=10`.

### Ejecución

Desde `backend/`:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

La primera vez se descarga el modelo de sentimiento (~1 GB, queda guardado en la caché de Hugging
Face). El servidor está listo cuando aparece `Application startup complete`.

Después abrir el dashboard: doble clic en `ui-mini/index.html`, o servirlo y entrar a
`http://127.0.0.1:8080`:

```bash
cd proyecto-final/ui-mini
python -m http.server 8080
```

El primer resumen aparece cuando se cierra la primera ventana (`WINDOW_SECONDS`). Otros endpoints:
`http://127.0.0.1:8000/health` (estado y cantidad de clientes conectados) y
`http://127.0.0.1:8000/docs` (documentación automática de FastAPI).

### Tests y estilo

Desde `backend/`:

```bash
python -m pytest
```

Se usan varias herramientas de testing:

- **pytest**: tests unitarios de cada módulo (`app/tests/`).
- **Test de integración** (`test_main.py`): levanta el servidor con la fuente simulada y se conecta por
  WebSocket, de punta a punta. Un servidor falso imita a la API de YouTube (`test_sources.py`).
- **Hypothesis** (`test_properties.py`): genera cientos de casos al azar y compara el cache LRU y las
  tendencias contra una versión ingenua, fácil de verificar a mano.
- **doctest**: los ejemplos de los docstrings (`>>>`) también se ejecutan como tests.

Cobertura de los tests (qué porcentaje del código ejecutan):

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Chequeo de estilo PEP 8 (configurado en `.flake8`, con líneas de hasta 99 caracteres):

```bash
python -m flake8 app scripts
```

### Benchmarks y profiling

Desde `backend/`:

```bash
python -m scripts.benchmarks
python -m scripts.profile_pipeline
python -m snakeviz pipeline.prof
```

`benchmarks` compara cada optimización contra la versión anterior; `profile_pipeline` usa cProfile
para mostrar en qué se va el tiempo, y `snakeviz` lo muestra de forma gráfica. Los resultados
están en [docs/rendimiento.md](docs/rendimiento.md).
