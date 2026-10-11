"""Đọc manifest, parse văn bản và ghi corpus.json."""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.config import CORPUS_PATH, DATA_RAW
from backend.app.corpus.parser import parse_legal_text

KIND_LABEL = {
    "luat": "Luật",
    "nghi-dinh": "Nghị định",
    "thong-tu": "Thông tư",
}


def _drop_form_restart(articles: list) -> list:
    kept = []
    last = 0
    for article in articles:
        if last >= 10 and article.article_no <= 2 and article.article_no < last:
            break
        kept.append(article)
        last = article.article_no
    return kept


def citation_label(kind: str, number: str, article_no: int, clause_no: int) -> str:
    head = KIND_LABEL.get(kind, "Văn bản")
    if clause_no == 0:
        return f"Điều {article_no} {head} số {number}"
    return f"Khoản {clause_no} Điều {article_no} {head} số {number}"


def build_corpus() -> dict:
    manifest = json.loads((DATA_RAW / "manifest.json").read_text(encoding="utf-8"))
    provisions: list[dict] = []
    documents: list[dict] = []
    for doc in manifest["documents"]:
        raw_path = DATA_RAW / doc["file"]
        parsed = parse_legal_text(raw_path.read_text(encoding="utf-8"))
        article_count = 0
        for chapter in parsed.chapters:
            articles = _drop_form_restart(chapter.articles)
            article_count += len(articles)
            for article in articles:
                for clause in article.clauses:
                    provision_id = f"{doc['id']}:d{article.article_no}:k{clause.clause_no}"
                    provisions.append(
                        {
                            "id": provision_id,
                            "document_id": doc["id"],
                            "document_title": doc["title"],
                            "document_number": doc["number"],
                            "kind": doc["kind"],
                            "in_force": doc["in_force"],
                            "expired_date": doc.get("expired_date"),
                            "expiry_note": doc.get("expiry_note"),
                            "source_url": doc["source_url"],
                            "chapter": chapter.label,
                            "chapter_title": chapter.title,
                            "article_no": article.article_no,
                            "article_title": article.title,
                            "clause_no": clause.clause_no,
                            "text": clause.full_text,
                            "citation": citation_label(
                                doc["kind"], doc["number"], article.article_no, clause.clause_no
                            ),
                        }
                    )
        documents.append({**doc, "article_count": article_count})
    return {
        "frozen_on": manifest["frozen_on"],
        "note": manifest["note"],
        "documents": documents,
        "provisions": provisions,
    }


def load_corpus() -> dict:
    if not CORPUS_PATH.exists():
        corpus = build_corpus()
        CORPUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        CORPUS_PATH.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
        return corpus
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def write_corpus(path: Path | None = None) -> dict:
    corpus = build_corpus()
    target = path or CORPUS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
    return corpus
