"""Okapi BM25 trên token đã bỏ dấu."""

from __future__ import annotations

import math
from collections import Counter

from backend.app.retrieval.text import tokenize


class BM25Index:
    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.docs = [tokenize(text) for text in texts]
        self.n = len(self.docs)
        self.avgdl = (sum(len(doc) for doc in self.docs) / self.n) if self.n else 0.0
        df: Counter[str] = Counter()
        for doc in self.docs:
            df.update(set(doc))
        self.df = df
        self.idf = {
            term: math.log(1 + (self.n - freq + 0.5) / (freq + 0.5))
            for term, freq in df.items()
        }

    def scores(self, query: str) -> list[float]:
        q_terms = tokenize(query)
        if not q_terms or not self.n:
            return [0.0] * self.n
        result = [0.0] * self.n
        for index, doc in enumerate(self.docs):
            if not doc:
                continue
            tf = Counter(doc)
            dl = len(doc)
            score = 0.0
            for term in q_terms:
                if term not in tf:
                    continue
                freq = tf[term]
                idf = self.idf.get(term, 0.0)
                denom = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                score += idf * (freq * (self.k1 + 1)) / denom
            result[index] = score
        return result

    def top(self, query: str, k: int) -> list[tuple[int, float]]:
        ranked = sorted(enumerate(self.scores(query)), key=lambda item: item[1], reverse=True)
        return [(index, score) for index, score in ranked[:k] if score > 0]
