"""Làm sạch bản trích toàn văn và ghi data/raw.

Nguồn đối chiếu ghi trong data/raw/manifest.json. Bản tiếng Anh trên trang
tổng hợp không được đưa vào kho.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from backend.app.config import DATA_RAW

CLOSING_ARTICLES = """
Chương IX
ĐIỀU KHOẢN THI HÀNH

Điều 132. Hiệu lực thi hành
1. Luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2015.
2. Luật hôn nhân và gia đình ngày 09 tháng 6 năm 2000 hết hiệu lực kể từ ngày Luật này có hiệu lực thi hành.

Điều 133. Quy định chi tiết và hướng dẫn thi hành
Chính phủ quy định chi tiết và hướng dẫn thi hành các điều, khoản được giao trong Luật.
"""


def _clean_law(text: str) -> str:
    """Giữ mặt chữ Luật 2014: bỏ chú thích hợp nhất 2025, không nuốt điều kế bên."""
    text = text.replace("Tòa án nhân dân khu vực", "Tòa án nhân dân cấp huyện")
    text = re.sub(r"(cấp huyện)\s+\d\s+(nơi cư trú)", r"\1 \2", text)
    kept = [raw for raw in text.splitlines() if "81/2025" not in raw and "203/2025" not in raw]
    cleaned = "\n".join(kept)
    if "Điều 132." not in cleaned:
        cleaned = cleaned.rstrip() + "\n" + CLOSING_ARTICLES
    return cleaned


def _slice_from_article_one(text: str, stop_markers: list[str]) -> str:
    start = text.find("Điều 1.")
    if start < 0:
        raise ValueError("Không thấy Điều 1.")
    end = len(text)
    for marker in stop_markers:
        at = text.find(marker, start + 10)
        if at > start:
            end = min(end, at)
    return text[start:end].strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--law", type=Path, required=True)
    parser.add_argument("--decree", type=Path, required=True)
    parser.add_argument("--circular", type=Path, required=True)
    args = parser.parse_args()
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    law = _clean_law(args.law.read_text(encoding="utf-8"))
    decree = _slice_from_article_one(
        args.decree.read_text(encoding="utf-8"),
        ["\nArticle ", "\nArticle\t", "APPENDIX"],
    )
    circular = _slice_from_article_one(
        args.circular.read_text(encoding="utf-8"),
        [
            "Nơi nhận",
            "Công nhận người có tên dưới đây",
            "\nArticle ",
            "Tải file đính kèm",
        ],
    )
    (DATA_RAW / "52-2014-QH13.txt").write_text(law, encoding="utf-8")
    (DATA_RAW / "126-2014-ND-CP.txt").write_text(decree, encoding="utf-8")
    (DATA_RAW / "02a-2015-TT-BTP.txt").write_text(circular, encoding="utf-8")
    manifest = {
        "frozen_on": "2026-10-11",
        "note": (
            "Kho đóng băng cho khóa luận. Câu chữ Luật 52/2014/QH13 lấy từ văn bản hợp nhất "
            "trình bày lại luật này; cụm 'Tòa án nhân dân khu vực' được trả về 'Tòa án nhân dân cấp huyện' "
            "theo chú thích sửa đổi của Luật 81/2025/QH15 để giữ mặt chữ năm 2014. "
            "Điều 132 và Điều 133 được ghép từ phần cuối luật vì bản trích dừng ở Điều 131. "
            "Thông tư 02a/2015/TT-BTP được CSDL quốc gia về pháp luật ghi nhận hết hiệu lực toàn bộ từ 02/01/2016; "
            "vẫn nằm trong kho theo phạm vi đồ án và được gắn cờ hết hiệu lực."
        ),
        "documents": [
            {
                "id": "52-2014-QH13",
                "kind": "luat",
                "number": "52/2014/QH13",
                "title": "Luật Hôn nhân và gia đình",
                "issuer": "Quốc hội",
                "issued_date": "2014-06-19",
                "effective_date": "2015-01-01",
                "in_force": True,
                "source_url": "https://vbpl.vn/TW/Pages/vbpq-van-ban-goc.aspx?ItemID=36870",
                "file": "52-2014-QH13.txt",
            },
            {
                "id": "126-2014-ND-CP",
                "kind": "nghi-dinh",
                "number": "126/2014/NĐ-CP",
                "title": "Nghị định quy định chi tiết một số điều và biện pháp thi hành Luật Hôn nhân và gia đình",
                "issuer": "Chính phủ",
                "issued_date": "2014-12-31",
                "effective_date": "2015-02-15",
                "in_force": True,
                "source_url": "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-126-2014-nd-cp-4232.htm",
                "file": "126-2014-ND-CP.txt",
            },
            {
                "id": "02a-2015-TT-BTP",
                "kind": "thong-tu",
                "number": "02a/2015/TT-BTP",
                "title": "Thông tư hướng dẫn thi hành một số điều của Nghị định số 126/2014/NĐ-CP về quan hệ hôn nhân và gia đình có yếu tố nước ngoài",
                "issuer": "Bộ Tư pháp",
                "issued_date": "2015-02-23",
                "effective_date": "2015-04-10",
                "in_force": False,
                "expired_date": "2016-01-02",
                "expiry_note": "CSDL quốc gia về pháp luật ghi nhận Thông tư hết hiệu lực toàn bộ từ 02/01/2016.",
                "source_url": "https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=59908",
                "file": "02a-2015-TT-BTP.txt",
            },
        ],
    }
    (DATA_RAW / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote raw corpus to {DATA_RAW}")


if __name__ == "__main__":
    main()
