"""Nạp OWL/TTL, bảng ánh xạ CSV và mở rộng SPARQL sang khoản luật."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS

from backend.app.config import MAPPING_PATH, ONTOLOGY_PATH
from backend.app.corpus.parser import fold_vi
from backend.app.retrieval.text import content_tokens

FL = Namespace("http://kltn.local/family-law#")
_PROVISION = re.compile(r"^(52-2014-QH13|126-2014-ND-CP|02a-2015-TT-BTP):d\d+:k\d+$")
_CITE = re.compile(
    r"(?:quy định tại|theo quy định tại|tại)\s+(?:khoản\s+(\d+)\s+)?(?:Điều)\s+(\d+)",
    re.IGNORECASE,
)


def provision_node(provision_id: str) -> URIRef:
    return URIRef(FL + "prov/" + provision_id.replace(":", "/"))


def concept_node(concept_id: str) -> URIRef:
    return URIRef(FL + concept_id)


@dataclass
class ConceptHit:
    concept_id: str
    label: str
    score: float


class OntologyIndex:
    def __init__(self, provisions: list[dict] | None = None) -> None:
        self.graph = Graph()
        self.graph.parse(ONTOLOGY_PATH, format="turtle")
        self._load_mapping()
        if provisions:
            self._add_textual_cites(provisions)
        self.concepts = self._read_concepts()
        self.provision_ids = self._read_provision_ids()

    def _bind(self, subject: str, predicate: str, obj: str) -> None:
        pred = URIRef(FL + predicate)
        self.graph.add((self._term(subject), pred, self._term(obj)))

    def _term(self, token: str) -> URIRef:
        if _PROVISION.match(token):
            node = provision_node(token)
            self.graph.add((node, RDF.type, FL.LegalProvision))
            self.graph.add((node, FL.provisionId, Literal(token)))
            return node
        return concept_node(token)

    def _load_mapping(self) -> None:
        if not MAPPING_PATH.exists():
            return
        with MAPPING_PATH.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                subject = row["subject"].strip()
                predicate = row["predicate"].strip()
                obj = row["object"].strip()
                if subject and predicate and obj:
                    self._bind(subject, predicate, obj)

    def _add_textual_cites(self, provisions: list[dict]) -> None:
        known = {item["id"] for item in provisions}
        by_article: dict[tuple[str, int], str] = {}
        for item in provisions:
            key = (item["document_id"], item["article_no"])
            current = by_article.get(key)
            if current is None or item["clause_no"] == 1 or (item["clause_no"] == 0 and current.endswith(":k0")):
                if current is None or item["clause_no"] == 1:
                    by_article[key] = item["id"]
        for item in provisions:
            for match in _CITE.finditer(item["text"]):
                clause = int(match.group(1) or 0)
                article = int(match.group(2))
                target = f"{item['document_id']}:d{article}:k{clause or 1}"
                if target not in known:
                    target = by_article.get((item["document_id"], article), "")
                if target and target != item["id"] and target in known:
                    self._bind(item["id"], "cites", target)

    def _read_concepts(self) -> list[dict]:
        rows = []
        for concept in self.graph.subjects(RDF.type, FL.LegalConcept):
            label = self.graph.value(concept, RDFS.label)
            alts = [str(value) for value in self.graph.objects(concept, SKOS.altLabel)]
            phrases = [str(label or ""), *alts]
            rows.append(
                {
                    "id": str(concept).rsplit("#", 1)[-1],
                    "label": str(label or ""),
                    "alts": alts,
                    "phrases": [
                        (phrase, fold_vi(phrase).lower().strip(), content_tokens(phrase))
                        for phrase in phrases
                        if phrase.strip()
                    ],
                }
            )
        rows.sort(key=lambda item: item["label"])
        return rows

    def _read_provision_ids(self) -> set[str]:
        return {str(value) for value in self.graph.objects(None, FL.provisionId)}

    def match(self, question: str, limit: int = 4) -> list[ConceptHit]:
        folded_q = fold_vi(question).lower()
        hits: list[ConceptHit] = []
        for concept in self.concepts:
            best = 0.0
            for _phrase, folded, _tokens in concept["phrases"]:
                if len(folded) < 3:
                    continue
                if folded in folded_q:
                    best = max(best, min(len(folded) / 12.0, 3.0))
            if best > 0:
                hits.append(ConceptHit(concept["id"], concept["label"], best))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:limit]

    def match_coverage(self, question: str, limit: int = 2) -> list[ConceptHit]:
        """Khớp khái niệm khi câu hỏi đảo thứ tự từ, ví dụ 'phân chia tài sản ... ly hôn'."""
        question_tokens = content_tokens(question)
        hits: list[ConceptHit] = []
        for concept in self.concepts:
            best = 0.0
            for _phrase, folded, tokens in concept["phrases"]:
                if len(tokens) < 3 or len(folded) < 12:
                    continue
                if tokens <= question_tokens:
                    best = max(best, min(len(folded) / 12.0, 3.0))
            if best >= 1.0:
                hits.append(ConceptHit(concept["id"], concept["label"], best))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:limit]

    def expand(self, concept_ids: list[str], limit: int = 12) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()

        def add(provision_id: str) -> None:
            if provision_id and provision_id not in seen:
                seen.add(provision_id)
                ordered.append(provision_id)

        for concept_id in concept_ids:
            node = concept_node(concept_id)
            direct = self.graph.query(
                """
                PREFIX fl: <http://kltn.local/family-law#>
                SELECT ?pid WHERE {
                  ?concept fl:regulatedBy ?prov .
                  ?prov fl:provisionId ?pid .
                }
                """,
                initBindings={"concept": node},
            )
            direct_ids = [str(row.pid) for row in direct]
            for provision_id in direct_ids:
                add(provision_id)
            if not direct_ids:
                continue
            neighbors = self.graph.query(
                """
                PREFIX fl: <http://kltn.local/family-law#>
                SELECT ?pid WHERE {
                  ?concept fl:regulatedBy ?prov .
                  ?prov fl:detailedBy|fl:cites|fl:hasException ?other .
                  ?other fl:provisionId ?pid .
                }
                """,
                initBindings={"concept": node},
            )
            for row in neighbors:
                add(str(row.pid))
            narrower = self.graph.query(
                """
                PREFIX fl: <http://kltn.local/family-law#>
                SELECT ?pid WHERE {
                  ?child fl:narrowerThan ?concept .
                  ?child fl:regulatedBy ?prov .
                  ?prov fl:provisionId ?pid .
                }
                """,
                initBindings={"concept": node},
            )
            for row in narrower:
                add(str(row.pid))
        return ordered[:limit]

    def concept_cards(self) -> list[dict]:
        cards = []
        for concept in self.concepts:
            provisions = self.expand([concept["id"]], limit=8)
            parents = [
                str(value).rsplit("#", 1)[-1]
                for value in self.graph.objects(concept_node(concept["id"]), FL.narrowerThan)
            ]
            cards.append({**concept, "broader": parents, "provisions": provisions})
        return cards
