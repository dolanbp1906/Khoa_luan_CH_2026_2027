"""Truy hồi lai: BM25, vector, ontology, hòa Reciprocal Rank Fusion."""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.ontology.graph import OntologyIndex
from backend.app.retrieval.bm25 import BM25Index
from backend.app.retrieval.dense import HashEmbedder, VectorIndex, build_embedder
from backend.app.retrieval.rrf import reciprocal_rank_fusion

MODES = ("bm25", "dense", "hybrid", "hybrid_ontology")


@dataclass
class Hit:
    provision_id: str
    score: float
    text: str
    citation: str
    document_id: str
    document_number: str
    document_title: str
    article_no: int
    article_title: str
    clause_no: int
    in_force: bool
    expiry_note: str | None
    source_url: str


class Retriever:
    def __init__(self, provisions: list[dict], ontology: OntologyIndex, vectors: VectorIndex, embedder) -> None:
        self.provisions = provisions
        self.by_id = {item["id"]: item for item in provisions}
        self.ontology = ontology
        self.vectors = vectors
        self.embedder = embedder
        self.bm25 = BM25Index([self._doc_text(item) for item in provisions])

    @staticmethod
    def _doc_text(item: dict) -> str:
        return " ".join(
            [
                item["article_title"],
                item["citation"],
                item["text"],
                item["chapter_title"],
            ]
        )

    def _pack(self, ranked_ids: list[tuple[str, float]], limit: int) -> list[Hit]:
        hits: list[Hit] = []
        for provision_id, score in ranked_ids[:limit]:
            item = self.by_id.get(provision_id)
            if not item:
                continue
            hits.append(
                Hit(
                    provision_id=item["id"],
                    score=score,
                    text=item["text"],
                    citation=item["citation"],
                    document_id=item["document_id"],
                    document_number=item["document_number"],
                    document_title=item["document_title"],
                    article_no=item["article_no"],
                    article_title=item["article_title"],
                    clause_no=item["clause_no"],
                    in_force=item["in_force"],
                    expiry_note=item.get("expiry_note"),
                    source_url=item["source_url"],
                )
            )
        return hits

    def _ids_from_scores(self, pairs: list[tuple[int, float]]) -> list[str]:
        return [self.provisions[index]["id"] for index, _score in pairs]

    def search(self, question: str, mode: str = "hybrid_ontology", limit: int = 8) -> tuple[list[Hit], list[dict], float]:
        if mode not in MODES:
            mode = "hybrid_ontology"
        pool = max(limit * 4, 20)
        bm25_ids = self._ids_from_scores(self.bm25.top(question, pool))
        dense_ids = self._ids_from_scores(self.vectors.top(self.embedder.embed_query(question), pool))
        concepts = self.ontology.match(question)
        strong = [hit for hit in concepts if hit.score >= 1.0][:2]
        strong_ids = {hit.concept_id for hit in strong}
        soft = [hit for hit in self.ontology.match_coverage(question) if hit.concept_id not in strong_ids][:2]
        chosen_concepts = strong if strong else soft
        onto_ids = self.ontology.expand([hit.concept_id for hit in strong]) if strong else []
        concept_payload = []
        linked_ids: list[str] = []
        for hit in chosen_concepts:
            provisions = self.ontology.expand([hit.concept_id], limit=6)
            linked_ids.extend(provisions)
            concept_payload.append(
                {
                    "id": hit.concept_id,
                    "label": hit.label,
                    "score": round(hit.score, 3),
                    "provisions": provisions,
                }
            )
        if mode == "bm25":
            fused = [(provision_id, 1.0 / (60 + rank)) for rank, provision_id in enumerate(bm25_ids, start=1)]
        elif mode == "dense":
            fused = [(provision_id, 1.0 / (60 + rank)) for rank, provision_id in enumerate(dense_ids, start=1)]
        elif mode == "hybrid":
            fused = reciprocal_rank_fusion([bm25_ids, dense_ids])
        else:
            fused = reciprocal_rank_fusion([bm25_ids, dense_ids, onto_ids])
        bm25_top = self.bm25.top(question, 1)
        lexical = bm25_top[0][1] if bm25_top else 0.0
        packed = self._pack(fused, limit)
        present = {hit.provision_id for hit in packed}
        extra = [(provision_id, 0.0) for provision_id in linked_ids if provision_id not in present]
        if extra:
            packed.extend(self._pack(extra, len(extra)))
        return packed, concept_payload, lexical

    @classmethod
    def build(cls, provisions: list[dict], ontology: OntologyIndex) -> "Retriever":
        embedder = build_embedder()
        cached = VectorIndex.load()
        if cached and cached.matrix.shape[0] == len(provisions) and cached.backend_name == embedder.name:
            vectors = cached
        else:
            matrix = embedder.embed_documents([cls._doc_text(item) for item in provisions])
            vectors = VectorIndex(matrix, embedder.name)
            vectors.save()
        return cls(provisions, ontology, vectors, embedder)


def fallback_embedder_name(retriever: Retriever) -> str:
    return getattr(retriever.embedder, "name", HashEmbedder.name)
