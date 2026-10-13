from collections import Counter

from app.trends import TrendingHashtags


def test_trending_accumulates_across_windows():
    trends = TrendingHashtags(seconds=60)
    trends.add(Counter({"ia": 2, "python": 1}), now=0)
    trends.add(Counter({"ia": 1}), now=10)
    assert trends.top(2) == [("ia", 3), ("python", 1)]


def test_trending_forgets_expired_windows():
    trends = TrendingHashtags(seconds=60)
    trends.add(Counter({"ia": 5}), now=0)
    trends.add(Counter({"python": 1}), now=61)   # la ventana de t=0 ya venció
    assert trends.top() == [("python", 1)]
    assert "ia" not in trends.totals              # no quedan claves en cero
