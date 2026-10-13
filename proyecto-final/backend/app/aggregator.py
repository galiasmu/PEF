"""Resumen de cada ventana: total, hashtags, tendencias y sentimiento promedio."""
import re
import time
from collections import Counter

from .trends import TrendingHashtags

# "#" seguido de letras/números/_ y que no esté pegado a una palabra (ej. "pagina#seccion").
HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)")
LABELS = ("positive", "neutral", "negative")


def extract_hashtags(text: str) -> list[str]:
    """Devuelve los hashtags del texto, en minúscula y sin el '#'.

    >>> extract_hashtags("Muy bueno #Python #IA!")
    ['python', 'ia']
    """
    return [tag.lower() for tag in HASHTAG_RE.findall(text)]


def summarize(window: list[dict], trends: TrendingHashtags) -> dict:
    """Resume una ventana de comentarios y actualiza las tendencias con sus hashtags."""
    tags = Counter(tag for comment in window for tag in extract_hashtags(comment["text"]))
    trends.add(tags, time.monotonic())

    n = max(len(window), 1)  # evita dividir por cero en una ventana vacía
    avg_sentiment = {label: sum(c["sentiment"][label] for c in window) / n for label in LABELS}
    return {
        "total_comments": len(window),
        "top_hashtags": tags.most_common(10),
        "trending": trends.top(10),
        "avg_sentiment": avg_sentiment,
    }
