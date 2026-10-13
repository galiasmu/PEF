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

## ¿Cómo funciona?

```
fuente ──► productor ──► cola (MAX_QUEUE) ──► ventanas de tiempo ──► sentimiento + resumen ──► WebSocket ──► dashboard
```

El pipeline arranca **una sola vez**, junto con el servidor, y reparte (*broadcast*) cada resumen a
todos los clientes conectados: no importa cuántas pestañas del dashboard estén abiertas, se consulta
a YouTube y se usa el modelo una sola vez por ventana.

1. La **fuente de datos** (`app/sources.py`) es un *generador asíncrono* que entrega, en cada consulta,
   un lote con los comentarios nuevos:
   - **YouTube:** consulta la API (`commentThreads`) con `aiohttp`, sin bloquear el servidor, y descarta
     los comentarios ya vistos.
   - **Simulada:** genera comentarios falsos, para probar el sistema sin API key.
2. El **pipeline** (`app/pipeline.py`) funciona con concurrencia (`asyncio`):
   - un **productor** corre como tarea aparte y pone cada comentario en una **cola**;
   - la cola tiene tamaño máximo (`MAX_QUEUE`): si se llena, el productor espera (*backpressure*);
   - el consumidor agrupa lo que sale de la cola en **ventanas de tiempo** de `WINDOW_SECONDS`
     segundos (emite la ventana aunque esté vacía).
3. El **análisis de sentimiento** (`app/sentiment.py`) procesa los comentarios de la ventana **por lote**:
   - el modelo recibe todos los textos juntos (3,2 veces más rápido que de a uno, medido con 64 comentarios);
   - corre **en otro hilo** (`asyncio.to_thread`), así no frena al productor mientras analiza;
   - los resultados se **memoizan** en un cache LRU (`app/cache.py`): un texto repetido no vuelve a
     pasar por el modelo;
   - si el modelo no se puede cargar, se avisa y se usa un análisis léxico simple (listas de palabras).
4. Se calcula el resumen de la ventana (`app/aggregator.py`): total, top de hashtags (con
   `collections.Counter`) y sentimiento promedio.
5. Las **tendencias** (`app/trends.py`) funcionan como un cache con vencimiento (TTL): cada ventana suma
   sus hashtags y, pasados `TREND_SECONDS` segundos, se descuenta sola. Las ventanas vencen en el
   mismo orden en que entraron, así que alcanza con una `deque` (FIFO).
6. El resumen se envía por **WebSocket** a todos los clientes (`app/main.py`), y el **dashboard**
   (`ui-mini/`) actualiza los gráficos: comentarios por ventana, sentimiento promedio, tendencias y
   hashtags de la ventana. Muestra solo las últimas 30 ventanas (la memoria del navegador no crece
   sin límite) y, si el backend se reinicia, se reconecta solo.

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
.venv\Scripts\activate
pip install -r requirements.txt
```

En Linux/Mac, activar el entorno con `source .venv/bin/activate`.

### Configuración

Copiar la plantilla `backend/.env.example` como `backend/.env` y completar la API key
y el ID del video. El `.env` no se sube al repositorio.

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
| `MAX_QUEUE` | `5000` | Tamaño máximo de las colas internas |
| `SENTIMENT_MODEL` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Modelo de Hugging Face para el sentimiento |

Toda la configuración se lee en un único lugar: `app/config.py`.

### Ejecución

Desde `backend/`:

```bash
uvicorn app.main:app --reload --port 8000
```

La primera vez se descarga el modelo de sentimiento (~1 GB, queda guardado en la caché de Hugging Face).

Después abrir el dashboard: doble clic en `ui-mini/index.html`, o servirlo y entrar a
`http://127.0.0.1:8080`:

```bash
cd proyecto-final/ui-mini
python -m http.server 8080
```

### Tests y estilo

Desde `backend/`, con el entorno activado:

```bash
pytest
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
pytest --cov=app --cov-report=term-missing
```

Chequeo de estilo PEP 8 (configurado en `.flake8`, con líneas de hasta 99 caracteres):

```bash
flake8 app scripts
```

### Benchmarks y profiling

Desde `backend/`:

```bash
python -m scripts.benchmarks
python -m scripts.profile_pipeline
snakeviz pipeline.prof
```

`benchmarks` compara cada optimización contra la versión anterior; `profile_pipeline` usa cProfile
para mostrar en qué se va el tiempo, y `snakeviz` lo muestra de forma gráfica. Los resultados
están en [docs/rendimiento.md](docs/rendimiento.md).
