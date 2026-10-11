"""Vector cục bộ. Mặc định hashing n-gram để chạy offline; đổi sang mô hình neural nếu cài thêm."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from backend.app.config import DATA_INDEX, EMBEDDING_BACKEND, EMBEDDING_MODEL
from backend.app.retrieval.text import tokenize


class HashEmbedder:
    name = "hash-ngram"

    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def _vec(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dim, dtype=np.float32)
        tokens = tokenize(text)
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            vector[int.from_bytes(digest, "little") % self.dim] += 1.0
        for left, right in zip(tokens, tokens[1:]):
            digest = hashlib.blake2b(f"{left} {right}".encode("utf-8"), digest_size=8).digest()
            vector[int.from_bytes(digest, "little") % self.dim] += 0.5
        norm = float(np.linalg.norm(vector))
        if norm:
            vector /= norm
        return vector

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.vstack([self._vec(text) for text in texts])

    def embed_query(self, text: str) -> np.ndarray:
        return self._vec(text)


class NeuralEmbedder:
    def __init__(self, model_name: str) -> None:
        from fastembed import TextEmbedding

        self.model_name = model_name
        self.name = model_name
        self._model = TextEmbedding(model_name=model_name)
        probe = list(self._model.embed(["query: probe"]))
        self.dim = len(probe[0])

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        prefixed = [f"passage: {text}" for text in texts]
        rows = [np.asarray(vector, dtype=np.float32) for vector in self._model.embed(prefixed)]
        return np.vstack(rows) if rows else np.zeros((0, self.dim), dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        vector = next(iter(self._model.embed([f"query: {text}"])))
        return np.asarray(vector, dtype=np.float32)


def build_embedder():
    backend = EMBEDDING_BACKEND.lower()
    if backend in {"fastembed", "neural", "e5"}:
        try:
            return NeuralEmbedder(EMBEDDING_MODEL)
        except Exception:
            return HashEmbedder()
    return HashEmbedder()


class VectorIndex:
    def __init__(self, matrix: np.ndarray, backend_name: str) -> None:
        self.matrix = matrix
        self.backend_name = backend_name

    def top(self, query_vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        if self.matrix.size == 0:
            return []
        scores = self.matrix @ query_vector
        order = np.argsort(-scores)[:k]
        return [(int(index), float(scores[index])) for index in order if scores[index] > 0]

    def save(self, path: Path | None = None) -> None:
        target = path or (DATA_INDEX / "vectors.npz")
        target.parent.mkdir(parents=True, exist_ok=True)
        np.savez(target, matrix=self.matrix, backend=np.array(self.backend_name))

    @classmethod
    def load(cls, path: Path | None = None) -> "VectorIndex | None":
        target = path or (DATA_INDEX / "vectors.npz")
        if not target.exists():
            return None
        data = np.load(target, allow_pickle=False)
        backend = str(data["backend"]) if "backend" in data else "unknown"
        return cls(data["matrix"], backend)
