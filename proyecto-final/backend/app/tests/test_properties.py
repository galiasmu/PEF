"""Tests basados en propiedades (Hypothesis).

Hypothesis genera cientos de casos al azar y verifica que las estructuras
eficientes den lo mismo que una versión ingenua: lenta, pero tan simple que
se puede verificar a mano.
"""
from collections import Counter

from hypothesis import given
from hypothesis import strategies as st

from app.cache import LRUCache
from app.trends import TrendingHashtags

keys = st.sampled_from("abcdef")


@given(st.lists(keys), st.integers(min_value=1, max_value=4))
def test_lru_matches_naive_version(puts, maxsize):
    cache = LRUCache(maxsize)
    naive = []  # claves ordenadas de menos a más reciente (O(n), pero obvio)
    for key in puts:
        cache.put(key, key)
        if key in naive:
            naive.remove(key)
        naive = (naive + [key])[-maxsize:]

    assert len(cache) == len(naive)
    assert all(cache.get(key) == key for key in naive)
    assert all(cache.get(key) is None for key in set("abcdef") - set(naive))


windows = st.lists(st.tuples(st.dictionaries(keys, st.integers(1, 5)), st.integers(0, 40)))


@given(windows)
def test_trends_match_naive_count(steps):
    trends = TrendingHashtags(seconds=60)
    now, history = 0, []
    for counts, elapsed in steps:
        now += elapsed
        trends.add(Counter(counts), now)
        history.append((now, counts))

    expected = Counter()
    for moment, counts in history:  # ingenuo: recorre toda la historia cada vez
        if now - moment <= 60:
            expected.update(counts)
    assert trends.totals == expected
