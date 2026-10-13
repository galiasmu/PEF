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
| `YOUTUBE_API_KEY` | — | Clave de la API de YouTube (obligatoria) |
| `TARGET_TYPE` | `video` | Tipo de objetivo |
| `TARGET_ID` | — | ID del video, lo que sigue a `watch?v=` en la URL (obligatorio) |
| `POLL_INTERVAL` | `5` | Segundos entre consultas a YouTube |
| `WINDOW_SECONDS` | `10` | Duración de cada ventana de análisis, en segundos |
| `MAX_QUEUE` | `5000` | Tamaño máximo de las colas internas |
| `SENTIMENT_MODEL` | `cardiffnlp/twitter-xlm-roberta-base-sentiment` | Modelo de Hugging Face para el sentimiento |

Toda la configuración se lee en un único lugar: `app/config.py`.

### Ejecución

Desde `backend/`:

```bash
uvicorn app.main:app --reload --port 8000
```

Después abrir `ui-mini/index.html` en el navegador (o servirlo con `npx live-server --port=8080`).

### Tests

Desde `backend/`, con el entorno activado:

```bash
pytest
```
