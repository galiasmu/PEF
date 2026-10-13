# Análisis en Tiempo Real de Redes Sociales

**Materia:** Programación Eficiente (PEF) — Universidad Blas Pascal
**Consigna:** Final PEF 2025, consigna 8 — *Sistema de Análisis en Tiempo Real de Redes Sociales*
**Autor:** Gali Asmuzi

---

## ¿Qué hace?

Recolecta los comentarios de un video de YouTube y los analiza en tiempo casi real.
Cada cierto intervalo (una *ventana de tiempo*) calcula:

- **Cantidad de comentarios** recibidos en la ventana.
- **Hashtags más usados** (top 10).
- **Sentimiento promedio** (positivo / neutral / negativo), usando un modelo de IA
  de procesamiento de lenguaje natural
  (`cardiffnlp/twitter-xlm-roberta-base-sentiment`, de Hugging Face `transformers`).

Los resultados se muestran en vivo en un **dashboard web**.

## ¿Cómo funciona?

```
YouTube Data API ──(consulta cada POLL_INTERVAL s)──► backend (FastAPI)
                                                       │ 1. descarta comentarios ya vistos
                                                       │ 2. analiza el sentimiento
                                                       │ 3. acumula en un buffer
                                                       │ 4. cada WINDOW_SECONDS agrega la ventana
                                                       ▼
                                          WebSocket /ws/metrics ──► dashboard (Chart.js)
```

1. El **backend** consulta periódicamente la API de YouTube (`commentThreads`) y toma los comentarios nuevos.
2. Cada comentario pasa por el **modelo de sentimiento**. Si el modelo no está disponible, se usa un
   análisis léxico simple (listas de palabras positivas y negativas).
3. Los comentarios se acumulan y, al cerrar cada **ventana de tiempo**, se calcula el resumen:
   total, top de hashtags (con `collections.Counter`) y sentimiento promedio.
4. El resumen se envía por **WebSocket** al dashboard, que actualiza los gráficos.

## Estructura

```
proyecto-final/
├── backend/
│   ├── app/          # código del backend (FastAPI)
│   │   └── tests/    # tests con pytest
│   └── requirements.txt
├── scripts/          # profiling
└── ui-mini/          # dashboard web (HTML + Chart.js)
```

## Cómo correrlo

### Requisitos

- Python 3.12
- Una API key de **YouTube Data API v3** ([cómo obtenerla](https://developers.google.com/youtube/v3/getting-started))

### Instalación

```bash
cd proyecto-final/backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt requests
```

En Linux/Mac, activar el entorno con `source .venv/bin/activate`.

### Configuración

Crear el archivo `backend/.env` (no se sube al repositorio):

```
YOUTUBE_API_KEY=tu_clave
TARGET_TYPE=video
TARGET_ID=id_del_video
POLL_INTERVAL=5
WINDOW_SECONDS=10
SENTIMENT_MODEL=cardiffnlp/twitter-xlm-roberta-base-sentiment
```

| Variable | Descripción |
|---|---|
| `YOUTUBE_API_KEY` | Clave de la API de YouTube |
| `TARGET_TYPE` | `video` |
| `TARGET_ID` | ID del video (lo que sigue a `watch?v=` en la URL) |
| `POLL_INTERVAL` | Segundos entre consultas a YouTube |
| `WINDOW_SECONDS` | Duración de cada ventana de análisis |
| `SENTIMENT_MODEL` | Modelo de Hugging Face para el sentimiento |

### Ejecución

Desde `backend/`:

```bash
uvicorn app.main:app --reload --port 8000
```

Después abrir `ui-mini/index.html` en el navegador (o servirlo con `npx live-server --port=8080`).

### Tests

```bash
cd proyecto-final/backend
pytest -q
```
