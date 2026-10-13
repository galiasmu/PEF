from typing import List, Dict, Any
from .utils_hashtags import count_hashtags

def aggregate_window(batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    texts = [b.get('text', '') for b in batch]
    hashtags_top = count_hashtags(texts, top_n=10)
    total = len(batch)
    return {
        'total_comments': total,
        'top_hashtags': hashtags_top,
    }
