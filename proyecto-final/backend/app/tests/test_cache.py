from app.cache import LRUCache


def test_lru_evicts_least_recently_used():
    cache = LRUCache(maxsize=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")       # "a" pasa a ser el más reciente
    cache.put("c", 3)    # se supera maxsize: sale "b", el menos usado

    assert cache.get("b") is None
    assert cache.get("a") == 1
    assert cache.get("c") == 3
    assert len(cache) == 2
