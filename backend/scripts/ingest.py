"""Đóng băng corpus JSON và chỉ mục vector."""

from __future__ import annotations

from backend.app.corpus.store import write_corpus
from backend.app.ontology.graph import OntologyIndex
from backend.app.retrieval.service import Retriever
from backend.scripts.emit_ontology import main as emit_ontology


def main() -> None:
    emit_ontology()
    corpus = write_corpus()
    ontology = OntologyIndex(corpus["provisions"])
    retriever = Retriever.build(corpus["provisions"], ontology)
    print(
        f"provisions={len(corpus['provisions'])} concepts={len(ontology.concepts)} "
        f"embedding={retriever.embedder.name}"
    )


if __name__ == "__main__":
    main()
