# Bossio–Asmuzi: YouTube Real‑Time Analytics (MVP)

Sistema que recolecta comentarios de YouTube y los analiza en tiempo (casi) real:
hashtags, tendencias y **sentimiento**. Incluye backend FastAPI + WebSocket y **interfaz gráfica** web.

## Requisitos
- Python 3.11+ (recomendado)
- Una API Key de **YouTube Data API v3**

## Configuración rápida
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env .env
# editar .env con tu YOUTUBE_API_KEY y el TARGET (video o channel)
uvicorn app.main:app --reload --port 8000
```

Luego abre `ui-mini/index.html` en el navegador. (Si preferís servirlo: `npx http-server ui-mini`)

## Variables de entorno (.env)
- `YOUTUBE_API_KEY`: tu clave
- `TARGET_TYPE`: `video` o `channel`
- `TARGET_ID`: id del video o canal
- `POLL_INTERVAL`: segundos entre polls (default 5)
- `WINDOW_SECONDS`: tamaño de ventana (default 10)
- `MAX_QUEUE`: tamaño máximo de cola (no usado intensivamente en MVP)
- `SENTIMENT_MODEL`: nombre del modelo (default `cardiffnlp/twitter-xlm-roberta-base-sentiment`)

## Tests
```bash
cd backend
pytest -q
```

## Profiling
```bash
cd backend
python -m cProfile -o stats.prof ../scripts/profile_entry.py
# Ver con snakeviz si lo tenés instalado: snakeviz stats.prof
```

Para correrlo finalmente, usamos el siguiente comando en directorio backend: 
 `uvicorn app.main:app --reload --port 8000`

luego en main `npx live-server --port=8080`

Se realizara un analisis de sentimientos de comentarios en tiempo real de un video o canal de YouTube,
para elegir el video lo configuramos en .env en la variable TARGET_ID y TARGET_TYPE (video o channel)