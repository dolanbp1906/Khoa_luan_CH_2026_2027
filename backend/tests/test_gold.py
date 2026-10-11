import json

from backend.app.config import EVAL_DIR
from backend.app.corpus.store import load_corpus
from backend.app.generation.service import answer_question
from backend.app.ontology.graph import OntologyIndex
from backend.app.retrieval.service import Retriever


def test_gold_ids_exist_and_cover_five_groups():
    corpus = load_corpus()
    known = {item["id"] for item in corpus["provisions"]}
    gold = json.loads((EVAL_DIR / "gold.json").read_text(encoding="utf-8"))
    assert len(gold) == 60
    groups = {item["group"] for item in gold}
    assert groups == {"single", "multi", "cross", "lay", "oos"}
    assert all(len([item for item in gold if item["group"] == group]) == 12 for group in groups)
    missing = [pid for item in gold for pid in item["gold_ids"] if pid not in known]
    assert missing == []


def test_age_question_retrieves_article_8_and_case_law_abstains():
    corpus = load_corpus()
    retriever = Retriever.build(corpus["provisions"], OntologyIndex(corpus["provisions"]))
    hits, concepts, lexical = retriever.search("Nam bao nhiêu tuổi thì được kết hôn?", "hybrid_ontology", 5)
    assert "52-2014-QH13:d8:k1" in [hit.provision_id for hit in hits]
    assert any(item["id"] == "DoTuoiKetHon" for item in concepts)
    generated = answer_question("Án lệ nào về quyền nuôi con?", hits, [], lexical)
    assert generated["abstain"] is True
