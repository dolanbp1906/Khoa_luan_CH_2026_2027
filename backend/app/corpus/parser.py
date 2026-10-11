"""Tách văn bản quy phạm Việt Nam thành Chương / Điều / Khoản / Điểm.

Đơn vị truy hồi là khoản. Điều không đánh số khoản được lưu khoản 0.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

CHAPTER_RE = re.compile(r"Chương\s+([IVXLCDM]+|\d+)\b")
ARTICLE_RE = re.compile(r"Điều\s+(\d+)\.\s*")
# Khoản: "1. " đứng trước chữ hoa tiếng Việt, không nuốt "01 tháng".
CLAUSE_RE = re.compile(
    r"(?:^|\s)(\d{1,2})\.\s+(?=[A-ZĐÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ])"
)
POINT_RE = re.compile(
    r"(?:^|\s)([a-zđ])\)\s+",
)
CAP_WORD_RE = re.compile(
    r"\s(?=[A-ZĐÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ][a-zà-ỹđ])"
)


@dataclass
class Point:
    label: str
    text: str


@dataclass
class Clause:
    clause_no: int
    text: str
    points: list[Point] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        if not self.points:
            return self.text.strip()
        parts = [self.text.strip()] if self.text.strip() else []
        parts.extend(f"{point.label}) {point.text.strip()}" for point in self.points)
        return " ".join(parts).strip()


@dataclass
class Article:
    article_no: int
    title: str
    clauses: list[Clause]


@dataclass
class Chapter:
    label: str
    title: str
    articles: list[Article]


@dataclass
class ParsedDocument:
    chapters: list[Chapter]


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("­", "")
    lines_out: list[str] = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^#+\s*", "", line)
        if re.fullmatch(r"\d{1,3}", line):
            continue
        line = re.sub(r"^\d{1,2}\s+(?=Điều\s+\d+\.)", "", line)
        line = re.sub(r"^\d{1,2}\s+(?=\d{1,2}\.\s)", "", line)
        line = re.sub(r"^\d{1,2}\s+(?=[a-zà-ỹđ])", "", line)
        line = re.sub(r"(THI HÀNH)\s+\d\s+(?=Điều\s)", r"\1 ", line)
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines_out.append(line)
    joined = "\n".join(lines_out)
    joined = re.sub(r"[ \t]+", " ", joined)
    joined = re.sub(r"\n(?!Chương\s)(?!Điều\s+\d+\.)", " ", joined)
    joined = re.sub(r"\s+\n", "\n", joined)
    joined = re.sub(r"(Chương\s+(?:[IVXLCDM]+|\d+)\b)", r"\n\1", joined)
    joined = re.sub(r"(Điều\s+\d+\.)", r"\n\1", joined)
    joined = re.sub(r"[ ]{2,}", " ", joined)
    joined = re.sub(r"\n{2,}", "\n", joined)
    return joined.strip()


_TITLE_CONNECTORS = {"của", "với", "và", "cho", "tại", "theo", "về", "trong", "giữa", "đối"}


def _body_capital_cut(rest: str) -> int | None:
    """Chữ hoa mở thân điều, bỏ tên riêng nối sau 'của/với/...'."""
    for match in CAP_WORD_RE.finditer(rest):
        before = rest[: match.start()].strip()
        words = before.split()
        prev = words[-1].lower().strip(",;:") if words else ""
        if prev in _TITLE_CONNECTORS:
            continue
        return match.start()
    return None


_TITLE_OPENERS = ("Trong ", "Luật này", "Nghị định này", "Thông tư này")


def _split_title_body(rest: str) -> tuple[str, str]:
    rest = rest.strip()
    clause_at = CLAUSE_RE.search(rest)
    # Có khoản thì tiêu đề dừng trước khoản 1, kể cả khi trong tiêu đề có "Nhà nước", "Việt Nam".
    cut = clause_at.start() if clause_at else _body_capital_cut(rest)
    if cut is None or cut <= 0:
        if CLAUSE_RE.match(rest):
            return "", rest
        return rest, ""
    title = rest[:cut].strip(" .")
    body = rest[cut:].strip()
    for opener in _TITLE_OPENERS:
        index = title.find(opener)
        if index > 8:
            body = f"{title[index:].strip()} {body}".strip()
            title = title[:index].strip(" .")
            break
    if not title:
        return "", rest
    return title, body


def _split_points(text: str) -> tuple[str, list[Point]]:
    matches = list(POINT_RE.finditer(text))
    if not matches:
        return text.strip(), []
    lead = text[: matches[0].start()].strip()
    points: list[Point] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        points.append(Point(label=match.group(1), text=text[match.end() : end].strip()))
    return lead, points


def _split_clauses(body: str) -> list[Clause]:
    body = body.strip()
    if not body:
        return []
    matches = list(CLAUSE_RE.finditer(body))
    # Chỉ nhận dãy khoản bắt đầu từ 1 và tăng dần, bỏ số năm/khoản dẫn chiếu xen giữa.
    selected: list[re.Match[str]] = []
    expected = 1
    for match in matches:
        number = int(match.group(1))
        if number == expected and number <= 30:
            selected.append(match)
            expected += 1
        elif number == 1 and not selected:
            selected.append(match)
            expected = 2
    if not selected:
        lead, points = _split_points(body)
        return [Clause(clause_no=0, text=lead, points=points)]
    clauses: list[Clause] = []
    preamble = body[: selected[0].start()].strip()
    if preamble:
        lead, points = _split_points(preamble)
        clauses.append(Clause(clause_no=0, text=lead, points=points))
    for index, match in enumerate(selected):
        end = selected[index + 1].start() if index + 1 < len(selected) else len(body)
        chunk = body[match.end() : end].strip()
        lead, points = _split_points(chunk)
        clauses.append(Clause(clause_no=int(match.group(1)), text=lead, points=points))
    return clauses


def parse_legal_text(text: str) -> ParsedDocument:
    normalized = normalize_text(text)
    chapter_parts = [part.strip() for part in re.split(r"\n(?=Chương\s+)", normalized) if part.strip()]
    chapters: list[Chapter] = []
    preamble_articles: list[Article] = []

    def parse_articles(blob: str) -> list[Article]:
        chunks = [chunk.strip() for chunk in re.split(r"\n(?=Điều\s+\d+\.)", blob) if chunk.strip()]
        articles: list[Article] = []
        for chunk in chunks:
            match = ARTICLE_RE.match(chunk)
            if not match:
                continue
            rest = chunk[match.end() :]
            title, body = _split_title_body(rest)
            articles.append(
                Article(
                    article_no=int(match.group(1)),
                    title=title.strip(),
                    clauses=_split_clauses(body if body else rest),
                )
            )
        return articles

    for part in chapter_parts:
        match = CHAPTER_RE.match(part)
        if not match:
            preamble_articles.extend(parse_articles(part))
            continue
        label = match.group(1)
        rest = part[match.end() :].strip()
        article_at = re.search(r"Điều\s+\d+\.", rest)
        if article_at:
            title = re.sub(r"\s+", " ", rest[: article_at.start()]).strip(" .")
            articles = parse_articles(rest[article_at.start() :])
        else:
            title = re.sub(r"\s+", " ", rest).strip(" .")
            articles = []
        chapters.append(Chapter(label=label, title=title, articles=articles))

    if preamble_articles:
        chapters.insert(0, Chapter(label="0", title="", articles=preamble_articles))
    merged: list[Chapter] = []
    for chapter in chapters:
        chapter.title = re.split(r"\s+Mục\s+", chapter.title, maxsplit=1)[0].strip()
        if merged and merged[-1].label == chapter.label and chapter.label != "0":
            merged[-1].articles.extend(chapter.articles)
        else:
            merged.append(chapter)
    return ParsedDocument(chapters=merged)


def fold_vi(text: str) -> str:
    """Bỏ dấu để so khớp câu hỏi nói không dấu."""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
