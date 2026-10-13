from app.aggregator import extract_hashtags, summarize
from app.trends import TrendingHashtags


def comment(text, positive=1.0, neutral=0.0, negative=0.0):
    return {"text": text, "sentiment": {"positive": positive, "neutral": neutral,
                                        "negative": negative}}


def test_extract_hashtags():
    assert extract_hashtags("hola #YouTube #IA!") == ["youtube", "ia"]
    assert extract_hashtags("pagina#seccion") == []      # pegado a una palabra: no es hashtag


def test_summarize_counts_and_averages():
    window = [comment("#a #a"), comment("#b", positive=0.0, negative=1.0)]
    summary = summarize(window, TrendingHashtags())

    assert summary["total_comments"] == 2
    assert summary["top_hashtags"][0] == ("a", 2)
    assert summary["trending"][0] == ("a", 2)
    assert summary["avg_sentiment"] == {"positive": 0.5, "neutral": 0.0, "negative": 0.5}


def test_summarize_empty_window():
    summary = summarize([], TrendingHashtags())
    assert summary["total_comments"] == 0
    assert summary["avg_sentiment"]["positive"] == 0.0
