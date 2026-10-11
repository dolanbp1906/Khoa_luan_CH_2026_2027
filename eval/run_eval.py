"""So Recall@5, MRR và tỷ lệ từ chối đúng của bốn chế độ truy hồi."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from backend.app.config import EVAL_DIR, ROOT
from backend.app.corpus.store import load_corpus
from backend.app.generation.service import answer_question
from backend.app.ontology.graph import OntologyIndex
from backend.app.retrieval.service import MODES, Retriever

GOLD_PATH = EVAL_DIR / "gold.json"
OUT_PATH = EVAL_DIR / "results.json"


def recall_at_k(retrieved: list[str], gold: list[str], k: int = 5) -> float:
    if not gold:
        return 1.0
    hit = len(set(retrieved[:k]) & set(gold))
    return hit / len(gold)


def mrr(retrieved: list[str], gold: list[str]) -> float:
    if not gold:
        return 1.0
    gold_set = set(gold)
    for rank, provision_id in enumerate(retrieved, start=1):
        if provision_id in gold_set:
            return 1.0 / rank
    return 0.0


def precision_at_k(retrieved: list[str], gold: list[str], k: int = 5) -> float:
    if not gold:
        return 1.0 if not retrieved[:k] else 0.0
    top = retrieved[:k]
    if not top:
        return 0.0
    return len(set(top) & set(gold)) / len(top)


def load_gold() -> list[dict]:
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def run(retriever: Retriever, gold: list[dict]) -> dict:
    report: dict = {"embedding": retriever.embedder.name, "modes": {}}
    for mode in MODES:
        rows = []
        by_group: dict[str, list[dict]] = defaultdict(list)
        for item in gold:
            hits, concepts, lexical = retriever.search(item["question"], mode=mode, limit=8)
            generated = answer_question(item["question"], hits, concepts, lexical)
            ids = [hit.provision_id for hit in hits]
            row = {
                "id": item["id"],
                "group": item["group"],
                "recall_at_5": recall_at_k(ids, item["gold_ids"]),
                "mrr": mrr(ids, item["gold_ids"]),
                "precision_at_5": precision_at_k(ids, item["gold_ids"]),
                "abstain": generated["abstain"],
                "abstain_correct": generated["abstain"] == item["expect_abstain"],
            }
            rows.append(row)
            by_group[item["group"]].append(row)

        def avg(values: list[float]) -> float:
            return sum(values) / len(values) if values else 0.0

        in_scope = [row for row in rows if row["group"] != "oos"]
        oos = [row for row in rows if row["group"] == "oos"]
        summary = {
            "recall_at_5": avg([row["recall_at_5"] for row in in_scope]),
            "mrr": avg([row["mrr"] for row in in_scope]),
            "precision_at_5": avg([row["precision_at_5"] for row in in_scope]),
            "abstain_accuracy": avg([1.0 if row["abstain_correct"] else 0.0 for row in rows]),
            "oos_abstain_rate": avg([1.0 if row["abstain"] else 0.0 for row in oos]),
            "groups": {},
        }
        for group, group_rows in by_group.items():
            scoped = group_rows if group == "oos" else group_rows
            summary["groups"][group] = {
                "recall_at_5": avg([row["recall_at_5"] for row in scoped]) if group != "oos" else None,
                "mrr": avg([row["mrr"] for row in scoped]) if group != "oos" else None,
                "abstain_accuracy": avg([1.0 if row["abstain_correct"] else 0.0 for row in scoped]),
            }
        report["modes"][mode] = {"summary": summary, "rows": rows}
    return report


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    corpus = load_corpus()
    ontology = OntologyIndex(corpus["provisions"])
    retriever = Retriever.build(corpus["provisions"], ontology)
    gold = load_gold()
    known = {item["id"] for item in corpus["provisions"]}
    missing = sorted({pid for item in gold for pid in item["gold_ids"] if pid not in known})
    if missing:
        raise SystemExit(f"Gold id không có trong kho: {missing}")
    report = run(retriever, gold)
    OUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [f"Embedding: {report['embedding']}", f"Câu hỏi: {len(gold)}"]
    for mode, payload in report["modes"].items():
        summary = payload["summary"]
        lines.append(
            f"{mode}: Recall@5={summary['recall_at_5']:.3f} MRR={summary['mrr']:.3f} "
            f"P@5={summary['precision_at_5']:.3f} từ_chối_đúng={summary['abstain_accuracy']:.3f}"
        )
        for group, scores in summary["groups"].items():
            recall = scores["recall_at_5"]
            recall_text = "n/a" if recall is None else f"{recall:.3f}"
            lines.append(f"  {group}: Recall@5={recall_text} từ_chối_đúng={scores['abstain_accuracy']:.3f}")
    text = "\n".join(lines)
    (EVAL_DIR / "results.txt").write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"Wrote {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
