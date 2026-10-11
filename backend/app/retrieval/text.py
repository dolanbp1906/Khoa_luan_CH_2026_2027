"""Tách từ tiếng Việt đơn giản cho BM25 và embedding n-gram."""

from __future__ import annotations

import re
import unicodedata

_STOP = {
    "cua", "va", "cac", "cho", "voi", "mot", "nhung", "trong", "theo", "nay",
    "khi", "thi", "la", "co", "khong", "duoc", "ve", "den", "tai", "neu",
    "hoac", "hay", "nhu", "se", "da", "do", "de", "tren", "duoi", "ra",
    "vao", "bi", "ma", "o", "lan", "sau", "truoc",
}
# Từ hỏi không nên tính là trùng nội dung với điều luật.
_FILLERS = {"sao", "nao", "gi", "bao", "nhieu", "the", "may", "phai", "muon"}
_TONE = {
    "\u0301": "s",
    "\u0300": "f",
    "\u0309": "r",
    "\u0303": "x",
    "\u0323": "j",
}
_TOKEN = re.compile(r"[0-9a-zA-Zà-ỹđ]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    tokens = []
    for match in _TOKEN.finditer(text):
        token = _base(match.group(0))
        if len(token) < 2 or token in _STOP:
            continue
        tokens.append(token)
    return tokens


def content_tokens(text: str, *, drop_fillers: bool = False) -> set[str]:
    """Giữ thanh điệu để tôi khác tối, tài khác tại."""
    found = set()
    for match in _TOKEN.finditer(text):
        raw = match.group(0)
        base = _base(raw)
        toned = _with_tone(raw)
        if len(base) < 3:
            continue
        # "tài" trùng mặt chữ với giới từ "tại" sau khi bỏ dấu, nhưng là từ nội dung.
        if base in _STOP and toned != "taif":
            continue
        if drop_fillers and base in _FILLERS:
            continue
        found.add(toned)
    return found


def _base(raw: str) -> str:
    text = raw.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text).lower()
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def _with_tone(raw: str) -> str:
    text = raw.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text).lower()
    tones: list[str] = []
    base: list[str] = []
    for ch in decomposed:
        if unicodedata.category(ch) == "Mn":
            mark = _TONE.get(ch)
            if mark:
                tones.append(mark)
            continue
        base.append(ch)
    token = "".join(base)
    if tones:
        token += "".join(tones)
    return token
