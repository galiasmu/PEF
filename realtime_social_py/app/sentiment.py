# app/sentiment.py
# Opción A (rápida, sin dependencias): heurística simple
NEG_WORDS = {"malo","triste","odio","feo","lento"}
POS_WORDS = {"bueno","feliz","amo","lindo","rápido"}

def score_text(text: str) -> float:
    t = text.lower()
    pos = sum(w in t for w in POS_WORDS)
    neg = sum(w in t for w in NEG_WORDS)
    return (pos - neg) / max(1, pos + neg) if (pos or neg) else 0.0

# Opción B: cambiar por transformers si querés un modelo real.
