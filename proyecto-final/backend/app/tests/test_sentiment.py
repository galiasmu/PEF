from app.sentiment import SentimentModel

def test_sentiment_smoke(monkeypatch):
    class Dummy:
        def __call__(self, text, **kw):
            return [[{"label":"POSITIVE","score":0.9},{"label":"NEGATIVE","score":0.1}]]
    sm = SentimentModel.__new__(SentimentModel)
    sm.pipeline = Dummy()
    assert sm.score("me encanta!")["positive"] > 0.5
