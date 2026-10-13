"""Análisis de sentimiento por lote, con memoización.

- El modelo de IA (Hugging Face ``transformers``) recibe todos los textos de
  una ventana juntos: procesar un lote es mucho más rápido que de a uno.
- Los resultados se guardan en un cache LRU: si un texto se repite (spam,
  comentarios copiados), no se vuelve a pasar por el modelo.
- Si el modelo no se puede cargar, se avisa y se usa un análisis léxico simple.
"""
import logging
import threading
from collections.abc import Callable

from .cache import LRUCache

log = logging.getLogger(__name__)

Scores = dict[str, float]  # {"positive": p, "neutral": n, "negative": g}

# Algunos modelos devuelven "LABEL_0/1/2" en lugar del nombre de la clase.
LABEL_ALIASES = {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}

POSITIVE_WORDS = {"genial", "buena", "excelente", "increible", "bien", "me encanta", "gracias", "love", "cool"}
NEGATIVE_WORDS = {"malo", "horrible", "odio", "asco", "feo", "wtf"}


def to_scores(result: list[dict]) -> Scores:
    """Pasa la salida del modelo (lista de ``{label, score}``) a un dict de scores."""
    scores = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
    for item in result:
        label = item["label"].lower()
        scores[LABEL_ALIASES.get(label, label)] = float(item["score"])
    return scores


def lexicon_scores(text: str) -> Scores:
    """Respaldo sin IA: cuenta palabras positivas y negativas conocidas."""
    t = text.lower()
    pos = sum(word in t for word in POSITIVE_WORDS)
    neg = sum(word in t for word in NEGATIVE_WORDS)
    if pos + neg == 0:
        return {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
    return {"positive": pos / (pos + neg), "neutral": 0.0, "negative": neg / (pos + neg)}


def load_model(model_name: str) -> Callable[[list[str]], list[Scores]]:
    """Carga el modelo y devuelve una función que analiza una lista de textos."""
    try:
        from transformers import pipeline
        pipe = pipeline("text-classification", model=model_name, top_k=None)
    except Exception as e:
        log.warning("No se pudo cargar el modelo %s (%s): se usa el análisis léxico",
                    model_name, type(e).__name__)
        return lambda texts: [lexicon_scores(t) for t in texts]

    def predict(texts: list[str]) -> list[Scores]:
        # max_length=512: límite del modelo; los comentarios más largos se recortan.
        results = pipe(texts, truncation=True, max_length=512, batch_size=32)
        return [to_scores(r) for r in results]

    return predict


class SentimentAnalyzer:
    """Analiza lotes de textos y memoiza los resultados en un cache LRU."""

    def __init__(self, predict: Callable[[list[str]], list[Scores]], cache_size: int = 10_000):
        self.predict = predict
        self.cache = LRUCache(cache_size)
        self._lock = threading.Lock()  # un solo hilo usa el modelo y el cache a la vez

    def analyze(self, texts: list[str]) -> list[Scores]:
        """Devuelve los scores de cada texto. Solo pasan por el modelo los que no están en cache."""
        with self._lock:
            results = {t: self.cache.get(t) for t in set(texts)}
            missing = [t for t, scores in results.items() if scores is None]
            if missing:
                for text, scores in zip(missing, self.predict(missing)):
                    results[text] = scores
                    self.cache.put(text, scores)
            return [results[t] for t in texts]
