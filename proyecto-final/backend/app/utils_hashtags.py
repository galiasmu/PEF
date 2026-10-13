\
import re
from collections import Counter
from typing import List, Tuple

HASHTAG_RE = re.compile(r"(?<!\w)#([\wáéíóúñçüÄÖÜßÀ-ÿ0-9_]{2,})", re.UNICODE)

def extract_hashtags(text: str) -> List[str]:
    return [h.lower() for h in HASHTAG_RE.findall(text or "")]

def count_hashtags(batch_texts: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
    c = Counter()
    for t in batch_texts:
        c.update(extract_hashtags(t))
    return c.most_common(top_n)
