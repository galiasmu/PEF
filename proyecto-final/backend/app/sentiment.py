from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import torch
from typing import Dict, List

class SentimentModel:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        device = 0 if torch.cuda.is_available() else -1
        self.pipeline = TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, device=device, top_k=None)

    def score(self, text: str) -> Dict[str, float]:
        result: List[Dict[str, float]] = self.pipeline(text, truncation=True, max_length=256)[0]  # list of {label, score}
        # Normalizar labels comunes
        norm = {}
        for d in result:
            label = d["label"].lower()
            score = float(d["score"])
            norm[label] = score
        # Mapear posibles nombres a positive/neutral/negative
        pos = norm.get("positive", norm.get("pos", 0.0))
        neg = norm.get("negative", norm.get("neg", 0.0))
        neu = norm.get("neutral", norm.get("neu", None))
        if neu is None:
            neu = max(0.0, 1.0 - pos - neg)
        return {"positive": pos, "neutral": neu, "negative": neg}
