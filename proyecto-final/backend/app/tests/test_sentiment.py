from app.sentiment import SentimentAnalyzer, lexicon_scores, to_scores

POSITIVE = {"positive": 1.0, "neutral": 0.0, "negative": 0.0}


def test_to_scores_maps_labels():
    result = [{"label": "LABEL_2", "score": 0.9}, {"label": "negative", "score": 0.1}]
    assert to_scores(result) == {"positive": 0.9, "neutral": 0.0, "negative": 0.1}


def test_lexicon_scores():
    assert lexicon_scores("me encanta, excelente")["positive"] == 1.0
    assert lexicon_scores("horrible")["negative"] == 1.0
    assert lexicon_scores("hola")["neutral"] == 1.0


def test_analyzer_memoizes_repeated_texts():
    calls = []

    def fake_predict(texts):
        calls.append(sorted(texts))
        return [POSITIVE for _ in texts]

    analyzer = SentimentAnalyzer(fake_predict)
    assert len(analyzer.analyze(["hola", "hola", "chau"])) == 3
    analyzer.analyze(["hola", "chau"])          # ya están en el cache

    assert calls == [["chau", "hola"]]          # el modelo se llamó una sola vez, sin repetidos
