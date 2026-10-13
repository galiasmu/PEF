"""Profiling con cProfile: ¿en qué se va el tiempo al procesar las ventanas?

Procesa 20 ventanas de 50 comentarios (sentimiento + resumen + tendencias) y
muestra cuánto tiempo acumula cada función del proyecto. Cada comentario tiene
un texto distinto: es el peor caso, porque la memoización no ayuda.

Guarda el perfil completo en pipeline.prof, para verlo gráficamente con:
    snakeviz pipeline.prof

Uso (desde backend/):  python -m scripts.profile_pipeline
"""
import cProfile
import pstats
import random

from app.aggregator import summarize
from app.config import settings
from app.sentiment import SentimentAnalyzer, load_model
from app.sources import fake_comment
from app.trends import TrendingHashtags


def make_windows(count: int = 20, size: int = 50) -> list[list[dict]]:
    rnd = random.Random(1)
    windows = []
    for w in range(count):
        window = [fake_comment(rnd, w * size + i) for i in range(size)]
        for comment in window:
            comment["text"] += f" ({comment['id']})"  # texto único: el cache no ayuda
        windows.append(window)
    return windows


def process(analyzer: SentimentAnalyzer, windows: list[list[dict]]) -> None:
    """Lo mismo que hace el pipeline con cada ventana, pero sin esperas de red."""
    trends = TrendingHashtags()
    for window in windows:
        scores = analyzer.analyze([comment["text"] for comment in window])
        for comment, sentiment in zip(window, scores):
            comment["sentiment"] = sentiment
        summarize(window, trends)


def main() -> None:
    analyzer = SentimentAnalyzer(load_model(settings.model_name))
    analyzer.predict(["calentamiento"])  # la primera llamada al modelo es más lenta
    windows = make_windows()

    profiler = cProfile.Profile()
    profiler.runcall(process, analyzer, windows)
    profiler.dump_stats("pipeline.prof")

    stats = pstats.Stats(profiler).strip_dirs().sort_stats("cumulative")
    stats.print_stats(r"(aggregator|cache|sentiment|trends)\.py")  # solo funciones del proyecto


if __name__ == "__main__":
    main()
