"""Sinh câu trả lời có trích dẫn. Không có khóa API thì trích nguyên văn khoản đã tìm được."""

from __future__ import annotations

import json
import re

import httpx

from backend.app.config import ABSTAIN_RRF_THRESHOLD, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.app.corpus.parser import fold_vi
from backend.app.retrieval.service import Hit
from backend.app.retrieval.text import content_tokens

_OOS_PATTERNS = [
    (r"an le|ban an da tuyen|tuyen an", "Án lệ và bản án không nằm trong kho."),
    (r"bo luat hinh su|phat tu|tu giam|truy cuu trach nhiem hinh su", "Trách nhiệm hình sự không thuộc Luật Hôn nhân và gia đình trong kho."),
    (r"thua ke|di chuc|di san thua ke", "Thừa kế thuộc Bộ luật Dân sự, ngoài kho đồ án."),
    (r"xu phat|vi pham hanh chinh|muc phat", "Mức xử phạt vi phạm hành chính không có trong kho."),
    (r"an phi|thoi han giai quyet ly hon|thoi hieu khoi kien", "Án phí và thời hạn tố tụng thuộc pháp luật tố tụng, ngoài kho."),
    (r"thu tuc nuoi con nuoi|luat nuoi con nuoi|ho so nhan con nuoi", "Thủ tục nuôi con nuôi thuộc Luật Nuôi con nuôi, ngoài kho."),
    (r"thu tuc giam ho|cu nguoi giam ho", "Thủ tục cử người giám hộ thuộc Bộ luật Dân sự, ngoài kho."),
    (r"dang ky khai sinh", "Đăng ký khai sinh thuộc pháp luật hộ tịch, ngoài kho, trừ thủ tục nhận cha mẹ con có yếu tố nước ngoài."),
    (r"giay to ket hon tai uy ban|thu tuc ket hon tai uy ban nhan dan xa", "Thủ tục hộ tịch trong nước không nằm trong kho."),
]


def out_of_scope_reason(question: str) -> str | None:
    folded = fold_vi(question).lower()
    foreign = "nuoc ngoai" in folded or "yeu to" in folded
    for pattern, reason in _OOS_PATTERNS:
        if re.search(pattern, folded):
            if "dang ky khai sinh" in pattern and foreign and "nhan" in folded:
                continue
            if "giay to ket hon" in pattern and foreign:
                continue
            return reason
    if not foreign and "ket hon" in folded and ("ubnd" in folded or "uy ban" in folded):
        return "Thủ tục đăng ký kết hôn tại UBND trong nước thuộc pháp luật hộ tịch, ngoài kho."
    if "thoi han" in folded and "ly hon" in folded and ("toa" in folded or "to tung" in folded):
        return "Thời hạn tố tụng ly hôn không có trong kho văn bản hôn nhân và gia đình."
    return None


def _overlap(question: str, hit: Hit) -> int:
    query = content_tokens(question, drop_fillers=True)
    if not query:
        return 0
    blob = f"{hit.article_title} {hit.text}"
    return len(query & content_tokens(blob, drop_fillers=True))


def select_hits(question: str, hits: list[Hit], concepts: list[dict]) -> list[Hit]:
    """Chỉ giữ khoản gắn khái niệm hoặc thực sự trùng từ với câu hỏi."""
    by_id = {hit.provision_id: hit for hit in hits}
    preferred: list[Hit] = []
    seen: set[str] = set()
    for concept in concepts:
        for provision_id in concept.get("provisions") or []:
            hit = by_id.get(provision_id)
            if hit and provision_id not in seen:
                seen.add(provision_id)
                preferred.append(hit)
    pool = preferred if preferred else list(hits)
    if not pool:
        return []
    query_size = len(content_tokens(question, drop_fillers=True))
    if not concepts:
        ranked = sorted(pool, key=lambda hit: _overlap(question, hit), reverse=True)
        best = _overlap(question, ranked[0])
        if best == 0 or (best <= 1 and query_size >= 3):
            return []
        floor = max(1, best - 1)
        return [hit for hit in ranked if _overlap(question, hit) >= floor][:2]
    best = max(_overlap(question, hit) for hit in preferred)
    if best == 0:
        return preferred[:2]
    floor = 1 if best == 1 else best - 1
    chosen = [hit for hit in preferred if _overlap(question, hit) >= floor]
    return (chosen or preferred[:2])[:3]


def focused_excerpt(question: str, text: str, limit: int = 280) -> str:
    query = content_tokens(question, drop_fillers=True)
    segments = [part.strip() for part in re.split(r"(?<=[.;])\s+", text) if part.strip()]
    if len(segments) <= 1:
        return _quote(text, limit)
    scored = [(len(query & content_tokens(part, drop_fillers=True)), index, part) for index, part in enumerate(segments)]
    best = max(score for score, _index, _part in scored)
    if best == 0:
        return _quote(text, limit)
    floor = max(1, best - 1)
    picked = [(index, part) for score, index, part in scored if score >= floor]
    picked.sort()
    return _quote(" ".join(part for _index, part in picked[:2]), limit)


def _quote(text: str, size: int = 420) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= size:
        return text
    return text[: size - 1].rsplit(" ", 1)[0] + "…"


def extractive_answer(question: str, hits: list[Hit], concepts: list[dict], lexical_score: float) -> dict:
    reason = out_of_scope_reason(question)
    chosen = [] if reason else select_hits(question, hits, concepts)
    weak = lexical_score < 0.8 and not concepts and (not hits or hits[0].score < ABSTAIN_RRF_THRESHOLD)
    if reason or not chosen or weak:
        return {
            "answer": reason
            or "Câu hỏi chưa khớp điều, khoản nào trong kho. Hãy nêu tình huống hôn nhân, tài sản, nuôi con hoặc cấp dưỡng.",
            "abstain": True,
            "abstain_reason": reason or "Không có khoản nào đủ gần với câu hỏi.",
            "citations": [],
            "generator": "extractive",
        }
    parts = []
    citations = []
    for hit in chosen:
        excerpt = focused_excerpt(question, hit.text)
        note = f" Lưu ý: {hit.expiry_note}" if not hit.in_force and hit.expiry_note else ""
        parts.append(f"{hit.citation}: {excerpt}{note}")
        citations.append(_citation_payload(hit))
    answer = " ".join(parts)
    return {
        "answer": answer,
        "abstain": False,
        "abstain_reason": None,
        "citations": citations,
        "generator": "extractive",
    }


def _citation_payload(hit: Hit) -> dict:
    return {
        "provision_id": hit.provision_id,
        "label": hit.citation,
        "document_title": hit.document_title,
        "document_number": hit.document_number,
        "article_no": hit.article_no,
        "article_title": hit.article_title,
        "clause_no": hit.clause_no,
        "quote": _quote(hit.text),
        "score": round(hit.score, 4),
        "in_force": hit.in_force,
        "expiry_note": hit.expiry_note,
        "source_url": hit.source_url,
    }


def _llm_answer(question: str, hits: list[Hit]) -> dict | None:
    if not LLM_API_KEY:
        return None
    context = []
    allowed = set()
    for hit in hits[:6]:
        allowed.add(hit.provision_id)
        flag = "" if hit.in_force else f" HẾT HIỆU LỰC. {hit.expiry_note or ''}"
        context.append(f"[{hit.provision_id}] {hit.citation}{flag}\n{hit.text}")
    prompt = (
        "Bạn hỗ trợ tra cứu Luật Hôn nhân và gia đình Việt Nam. "
        "Chỉ dùng các đoạn được cung cấp. Không bịa điều luật. "
        "Nếu đoạn không chứa căn cứ, hãy từ chối. "
        "Trả về JSON với khóa answer, abstain, abstain_reason, citations. "
        "Mỗi citation có provision_id nằm trong danh sách đoạn và quote là trích ngắn.\n\n"
        f"Câu hỏi: {question}\n\nĐoạn:\n" + "\n\n".join(context)
    )
    url = LLM_BASE_URL.rstrip("/") + "/chat/completions"
    try:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {LLM_API_KEY}"},
            json={
                "model": LLM_MODEL,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": "Chỉ trả JSON hợp lệ, tiếng Việt."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError):
        return None
    match = re.search(r"\{.*\}", content, re.S)
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    raw_cites = payload.get("citations") or []
    citations = []
    by_id = {hit.provision_id: hit for hit in hits}
    for cite in raw_cites:
        provision_id = str(cite.get("provision_id", ""))
        if provision_id not in allowed or provision_id not in by_id:
            continue
        item = _citation_payload(by_id[provision_id])
        if cite.get("quote"):
            item["quote"] = _quote(str(cite["quote"]))
        citations.append(item)
    abstain = bool(payload.get("abstain")) or not citations
    return {
        "answer": str(payload.get("answer") or "").strip(),
        "abstain": abstain,
        "abstain_reason": payload.get("abstain_reason"),
        "citations": [] if abstain else citations,
        "generator": "llm",
    }


def answer_question(question: str, hits: list[Hit], concepts: list[dict], lexical_score: float) -> dict:
    reason = out_of_scope_reason(question)
    if reason:
        return {
            "answer": reason,
            "abstain": True,
            "abstain_reason": reason,
            "citations": [],
            "generator": "scope",
        }
    chosen = select_hits(question, hits, concepts)
    if not chosen:
        return extractive_answer(question, hits, concepts, lexical_score)
    generated = _llm_answer(question, chosen)
    if generated and generated["answer"]:
        return generated
    return extractive_answer(question, hits, concepts, lexical_score)
