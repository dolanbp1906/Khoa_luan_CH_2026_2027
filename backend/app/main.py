"""API tra cứu Luật Hôn nhân và gia đình."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.corpus.store import load_corpus
from backend.app.generation.service import answer_question
from backend.app.ontology.graph import OntologyIndex
from backend.app.retrieval.service import MODES, Retriever

app = FastAPI(title="Tra cứu Luật Hôn nhân và gia đình", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_state: dict = {}


def get_state() -> dict:
    if "retriever" not in _state:
        corpus = load_corpus()
        ontology = OntologyIndex(corpus["provisions"])
        retriever = Retriever.build(corpus["provisions"], ontology)
        _state["corpus"] = corpus
        _state["ontology"] = ontology
        _state["retriever"] = retriever
    return _state


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    mode: str = "hybrid_ontology"


@app.get("/api/health")
def health() -> dict:
    state = get_state()
    corpus = state["corpus"]
    return {
        "ok": True,
        "provisions": len(corpus["provisions"]),
        "documents": [doc["id"] for doc in corpus["documents"]],
        "concepts": len(state["ontology"].concepts),
        "embedding": state["retriever"].embedder.name,
        "modes": list(MODES),
    }


@app.post("/api/ask")
def ask(body: AskRequest) -> dict:
    state = get_state()
    mode = body.mode if body.mode in MODES else "hybrid_ontology"
    hits, concepts, lexical = state["retriever"].search(body.question.strip(), mode=mode, limit=8)
    generated = answer_question(body.question.strip(), hits, concepts, lexical)
    return {
        "question": body.question.strip(),
        "mode": mode,
        "concepts": concepts,
        **generated,
        "disclaimer": "Công cụ hỗ trợ tra cứu văn bản, không phải tư vấn pháp lý.",
    }


@app.get("/api/concepts")
def concepts() -> dict:
    cards = get_state()["ontology"].concept_cards()
    provisions = {item["id"]: item for item in get_state()["corpus"]["provisions"]}
    payload = []
    for card in cards:
        linked = []
        for provision_id in card["provisions"]:
            item = provisions.get(provision_id)
            if not item:
                continue
            linked.append(
                {
                    "provision_id": provision_id,
                    "label": item["citation"],
                    "article_title": item["article_title"],
                }
            )
        payload.append(
            {
                "id": card["id"],
                "label": card["label"],
                "alts": card["alts"],
                "broader": card["broader"],
                "provisions": linked,
            }
        )
    return {"concepts": payload}


@app.get("/api/provisions/{provision_id}")
def provision(provision_id: str) -> dict:
    item = next(
        (row for row in get_state()["corpus"]["provisions"] if row["id"] == provision_id),
        None,
    )
    if not item:
        return {"found": False}
    return {"found": True, "provision": item}
