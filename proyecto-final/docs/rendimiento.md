# Rendimiento: mediciones de antes y después

Cada optimización del proyecto se midió contra la versión anterior (o contra la alternativa
ingenua). Los resultados dependen de la máquina; estos se tomaron en un Intel Core i5-12400 con
32 GB de RAM, Python 3.12, sin GPU.

Para reproducirlos, desde `backend/`:

```bash
python -m scripts.benchmarks
python -m scripts.profile_pipeline
```

## Benchmarks (`scripts/benchmarks.py`)

| Optimización | Antes | Después | Mejora |
|---|---|---|---|
| Cache con 10.000 inserciones (TTLCache O(n) → LRUCache O(1)) | 934,95 ms | 3,52 ms | 266x |
| Memoria para recordar 300.000 comentarios vistos (set → SeenIds) | 24,78 MB | 1,68 MB | 15x |
| Tendencias durante 1 hora de ventanas (desde cero → incremental) | 12,04 ms | 5,65 ms | 2x |
| Sentimiento de 64 comentarios (de a uno → por lote) | 1.595,21 ms | 531,43 ms | 3x |
| Sentimiento de 64 comentarios ya vistos (por lote → con memoización) | 549,15 ms | 0,03 ms | 17.161x |
| Pausa máxima del servidor mientras analiza (en el loop → en otro hilo) | 543,47 ms | 16,56 ms | 33x |

Qué mide cada fila:

1. **Cache.** El `TTLCache` original buscaba el elemento más viejo recorriendo todo el diccionario
   cada vez que se llenaba (O(n)). El `LRUCache` usa un `OrderedDict`: sacar el más viejo es O(1).
2. **Memoria de comentarios vistos.** El original guardaba los IDs en un `set` que crece sin límite.
   `SeenIds` (`set` + `deque`) recuerda solo los últimos 10.000: la memoria queda acotada aunque el
   servidor corra días.
3. **Tendencias.** Recalcular desde cero recorre toda la historia en cada ventana (O(n) por ventana);
   `TrendingHashtags` solo suma la ventana nueva y descuenta las vencidas. Con una hora de datos la
   diferencia es chica (2x), pero la versión desde cero empeora cuanto más tiempo corre el servidor,
   y la incremental no.
4. **Sentimiento por lote.** El modelo procesa los 64 textos juntos en lugar de llamarlo 64 veces.
5. **Memoización.** Un texto que ya se analizó sale del cache LRU sin pasar por el modelo.
6. **Modelo en otro hilo.** Mientras el modelo analiza, el servidor tiene que seguir atendiendo
   (traer comentarios, responder a los clientes). Se mide la pausa más larga del *event loop*: con el
   modelo en el loop, el servidor queda congelado medio segundo; con `asyncio.to_thread`, la pausa
   máxima baja a ~17 ms.

## Profiling (`scripts/profile_pipeline.py`)

Procesamiento de 20 ventanas de 50 comentarios, todos con texto distinto (peor caso: la memoización
no ayuda), medido con **cProfile**. Funciones del proyecto ordenadas por tiempo acumulado:

| Función | Llamadas | Tiempo acumulado | % del total |
|---|---|---|---|
| `sentiment.py: analyze` | 20 | 11,04 s | 99,9 % |
| `sentiment.py: predict` (el modelo) | 20 | 11,04 s | 99,9 % |
| `aggregator.py: summarize` (hashtags, promedios, tendencias) | 20 | 0,005 s | < 0,1 % |
| `cache.py: put` | 1.000 | 0,001 s | < 0,1 % |

**Conclusión:** casi todo el tiempo se va en el modelo de IA. Por eso las optimizaciones se
concentraron ahí (por lote, memoización y en otro hilo), y no en el conteo de hashtags, que ya es
despreciable. Es la idea de "evitar la optimización prematura": primero medir y después optimizar
donde está el cuello de botella.

El perfil completo queda en `backend/pipeline.prof` y se puede ver gráficamente con
[snakeviz](https://jiffyclub.github.io/snakeviz/):

```bash
snakeviz pipeline.prof
```
