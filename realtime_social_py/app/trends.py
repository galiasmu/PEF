# app/trends.py
from collections import Counter
import heapq, time

class TrendTopK:
    def __init__(self, k=10, ttl_sec=60):
        self.k = k
        self.ttl = ttl_sec
        self.acc = Counter()
        self.decay = []  # [(expire_ts, tag, count)]

    def ingest(self, tags: list[str], ts: float):
        for t in tags:
            self.acc[t] += 1
            heapq.heappush(self.decay, (ts + self.ttl, t, 1))

    def sweep(self, now: float):
        while self.decay and self.decay[0][0] <= now:
            _, t, c = heapq.heappop(self.decay)
            self.acc[t] -= c
            if self.acc[t] <= 0:
                del self.acc[t]

    def topk(self):
        return heapq.nlargest(self.k, self.acc.items(), key=lambda x: x[1])
